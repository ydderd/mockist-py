"""Harness — routes tool boundary calls through stubs and cassettes."""

from __future__ import annotations

import os
import time
import warnings
from datetime import datetime, timezone
from typing import Any

from mockist.async_utils import await_maybe
from mockist.cassette.io import load_cassette_entries, write_cassette
from mockist.cassette.redact import default_redactor
from mockist.cassette.registry import register_pending_save
from mockist.cassette.replay import CassetteResolver, create_cassette_resolver
from mockist.deep_equal import deep_equal
from mockist.identity import identify
from mockist.recorder import Recorder
from mockist.registry import ResettableResolver, predicate_resolver
from mockist.types import (
    Call,
    CallKind,
    CassetteState,
    Redactor,
    Resolver,
    SequenceStubState,
    Stub,
    UnhandledPolicy,
)


class Harness:
    def __init__(
        self,
        *,
        stubs: list[Stub] | None = None,
        resolvers: list[Resolver] | None = None,
        on_unhandled: UnhandledPolicy = "passthrough",
        redact: Redactor | None = None,
        cassette: str | None = None,
    ) -> None:
        self._stub_resolver: ResettableResolver = predicate_resolver(stubs or [])
        self._reset_resolvers: list[Any] = [self._stub_resolver.reset]
        self._cassette_path = cassette
        self.recording = bool(cassette) and bool(os.environ.get("MOCKIST_RECORD"))
        self._cassette: CassetteResolver | None = None
        cassette_resolvers: list[Resolver] = []

        if cassette and not self.recording:
            entries = load_cassette_entries(cassette)
            self._cassette = create_cassette_resolver(entries)
            cassette_resolvers.append(self._cassette.resolve)
            self._reset_resolvers.append(self._cassette.reset)

        self.resolvers: list[Resolver] = [
            self._stub_resolver,
            *cassette_resolvers,
            *(resolvers or []),
        ]

        if self.recording and on_unhandled == "error":
            warnings.warn(
                f'mockist: recording "{cassette}" — ignoring on_unhandled:"error" so real tools run.',
                stacklevel=2,
            )
        self._on_unhandled: UnhandledPolicy = (
            "passthrough" if self.recording else on_unhandled
        )
        recorder_redact = redact or (default_redactor if self.recording else None)
        self._recorder = Recorder(recorder_redact)
        self._cassette_save_buffer: list[Call] = []

        if self.recording:
            register_pending_save(self.save)

    @property
    def trajectory(self) -> list[Call]:
        return self._recorder.trajectory

    def calls_to(self, name: str) -> list[Call]:
        return [call for call in self.trajectory if call.name == name]

    def called_with(self, name: str, input: Any) -> bool:
        return any(call.name == name and deep_equal(call.input, input) for call in self.trajectory)

    def sequence_state(self) -> list[SequenceStubState]:
        return self._stub_resolver.sequence_state()

    def cassette_state(self) -> CassetteState:
        base = self._cassette.state() if self._cassette else {"matched": [], "missed": [], "unused": []}
        return CassetteState(
            path=self._cassette_path or "",
            entries=list(self._cassette.entries) if self._cassette else [],
            matched=base["matched"],
            missed=base["missed"],
            unused=base["unused"],
        )

    def save(self) -> None:
        if not self.recording or not self._cassette_path or not self._cassette_save_buffer:
            return
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        write_cassette(self._cassette_path, self._cassette_save_buffer, now=now)
        self._cassette_save_buffer.clear()

    def reset(self) -> None:
        self._recorder.reset()
        for reset in self._reset_resolvers:
            reset()

    def record_call(
        self,
        kind: CallKind,
        name: str,
        input: Any,
        *,
        stubbed: bool = True,
        output: Any | None = None,
        error: Any | None = None,
    ) -> None:
        key = identify(kind, name, input)
        self._recorder.record(
            Call(
                kind=kind,
                name=name,
                input=input,
                key=key,
                ts=time.time(),
                stubbed=stubbed,
                output=output,
                error=error,
            )
        )

    def capture_call(
        self,
        kind: CallKind,
        name: str,
        input: Any,
        *,
        stubbed: bool,
        output: Any | None = None,
        error: Any | None = None,
    ) -> None:
        key = identify(kind, name, input)
        self._push(kind, name, input, key, stubbed=stubbed, output=output, error=error)

    async def resolve_call(
        self,
        kind: CallKind,
        name: str,
        input: Any,
    ) -> dict[str, Any]:
        for resolve in self.resolvers:
            hit = resolve(_resolver_input(kind, name, input))
            if not hit:
                continue
            if hit.passthrough:
                return {"matched": True, "passthrough": True}
            return {"matched": True, "produce": lambda h=hit: await_maybe(h.produce())}
        if self._on_unhandled == "error":
            error = Exception(
                f'mockist: unhandled {kind} call "{name}" (on_unhandled: \'error\')'
            )
            self.record_call(kind, name, input, stubbed=False, error=error)
            raise error
        if self._on_unhandled == "warn":
            warnings.warn(
                f'mockist: unhandled {kind} call "{name}" — passing through',
                stacklevel=2,
            )
        return {"matched": False}

    async def dispatch(
        self,
        kind: CallKind,
        name: str,
        input: Any,
        original: Any,
    ) -> Any:
        key = identify(kind, name, input)
        defer_to_original = False

        for resolve in self.resolvers:
            hit = resolve(_resolver_input(kind, name, input))
            if not hit:
                continue
            if hit.passthrough:
                defer_to_original = True
                break
            try:
                output = await await_maybe(hit.produce())
                self._push(kind, name, input, key, stubbed=True, output=output)
                return output
            except Exception as error:
                self._push(kind, name, input, key, stubbed=True, error=error)
                raise

        if not defer_to_original and self._on_unhandled == "error":
            error = Exception(
                f'mockist: unhandled {kind} call "{name}" (on_unhandled: \'error\')'
            )
            self._push(kind, name, input, key, stubbed=False, error=error)
            raise error
        if not defer_to_original and self._on_unhandled == "warn":
            warnings.warn(
                f'mockist: unhandled {kind} call "{name}" — passing through',
                stacklevel=2,
            )

        try:
            output = await await_maybe(original() if callable(original) else original)
            self._push(kind, name, input, key, stubbed=False, output=output)
            return output
        except Exception as error:
            self._push(kind, name, input, key, stubbed=False, error=error)
            raise

    def _push(
        self,
        kind: CallKind,
        name: str,
        input: Any,
        key: str,
        *,
        stubbed: bool,
        output: Any | None = None,
        error: Any | None = None,
    ) -> None:
        self._recorder.record(
            Call(
                kind=kind,
                name=name,
                input=input,
                key=key,
                ts=time.time(),
                stubbed=stubbed,
                output=output,
                error=error,
            )
        )
        if self.recording:
            self._cassette_save_buffer.append(self.trajectory[-1])


def _resolver_input(kind: CallKind, name: str, input: Any):
    from mockist.types import ResolverInput

    return ResolverInput(kind=kind, name=name, input=input)


def create_harness(
    *,
    stubs: list[Stub] | None = None,
    resolvers: list[Resolver] | None = None,
    on_unhandled: UnhandledPolicy = "passthrough",
    redact: Redactor | None = None,
    cassette: str | None = None,
) -> Harness:
    return Harness(
        stubs=stubs,
        resolvers=resolvers,
        on_unhandled=on_unhandled,
        redact=redact,
        cassette=cassette,
    )
