"""Stub registry and matching."""

from __future__ import annotations

from collections.abc import Awaitable
from typing import Any

from mockist.deep_equal import deep_equal
from mockist.errors import SequenceExhaustedError
from mockist.types import Resolution, ResolverInput, SequenceStubState, Stub


def define_stubs(stubs: list[Stub]) -> list[Stub]:
    return stubs


class ResettableResolver:
    def __init__(self, stubs: list[Stub]) -> None:
        self._stubs = stubs
        self._cursors: dict[int, int] = {}
        self._drained: dict[int, int] = {}

    def reset(self) -> None:
        self._cursors.clear()
        self._drained.clear()

    def sequence_state(self) -> list[SequenceStubState]:
        states: list[SequenceStubState] = []
        for stub in self._stubs:
            sequence = stub.get("sequence")
            if not sequence:
                continue
            stub_id = id(stub)
            length = len(sequence)
            cursor = self._cursors.get(stub_id, 0)
            states.append(
                SequenceStubState(
                    name=stub["name"],
                    kind=stub.get("kind", "tool"),
                    length=length,
                    consumed=min(cursor, length),
                    exhausted=self._drained.get(stub_id, 0) > 0,
                )
            )
        return states

    def __call__(self, call: ResolverInput) -> Resolution | None:
        kind, name, input = call.kind, call.name, call.input
        for stub in self._stubs:
            if stub["name"] != name:
                continue
            stub_kind = stub.get("kind")
            if stub_kind is not None and stub_kind != kind:
                continue

            match_fn = stub.get("match")
            if match_fn is not None:
                matches = match_fn(input)
            elif "args" in stub:
                matches = deep_equal(input, stub["args"])
            else:
                matches = True
            if not matches:
                continue

            sequence = stub.get("sequence")
            if sequence is not None:
                return self._resolve_sequence_step(stub, input)
            if "result" not in stub:
                return Resolution(
                    produce=lambda: (_ for _ in ()).throw(
                        MockistStubError(f'mockist: stub "{name}" must define result or sequence')
                    )
                )
            stub_result = stub["result"]
            return Resolution(produce=lambda r=stub_result: produce_result(r, input))
        return None

    def _resolve_sequence_step(self, stub: Stub, input: Any) -> Resolution:
        sequence = stub.get("sequence") or []
        name = stub["name"]
        stub_id = id(stub)
        if len(sequence) == 0:
            return Resolution(
                produce=lambda: (_ for _ in ()).throw(
                    MockistStubError(f'mockist: sequence stub "{name}" must include at least one step')
                )
            )

        cursor = self._cursors.get(stub_id, 0)
        on_exhausted = stub.get("on_sequence_exhausted", "error")
        if cursor >= len(sequence) and on_exhausted == "passthrough":
            self._drained[stub_id] = self._drained.get(stub_id, 0) + 1
            return Resolution(passthrough=True, produce=_passthrough_produced)

        def produce() -> Any | Awaitable[Any]:
            cur = self._cursors.get(stub_id, 0)
            if cur >= len(sequence):
                self._drained[stub_id] = self._drained.get(stub_id, 0) + 1
                if on_exhausted == "repeat-last":
                    last = sequence[-1]
                    if "error" in last:
                        raise last["error"]
                    return produce_result(last.get("result"), input)
                raise SequenceExhaustedError(
                    f'mockist: sequence stub "{name}" exhausted after {len(sequence)} calls'
                )
            step = sequence[cur]
            self._cursors[stub_id] = cur + 1
            if "error" in step:
                raise step["error"]
            return produce_result(step.get("result"), input)

        return Resolution(produce=produce)


class MockistStubError(Exception):
    pass


def predicate_resolver(stubs: list[Stub]) -> ResettableResolver:
    return ResettableResolver(stubs)


def _passthrough_produced() -> None:
    raise RuntimeError("mockist: passthrough resolution should defer to the real tool, not produce")


def produce_result(result: Any, input: Any) -> Any | Awaitable[Any]:
    if callable(result):
        return result(input)
    return result
