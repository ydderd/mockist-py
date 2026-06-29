"""Domain types for mockist."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, Literal, TypeAlias

CallKind = Literal["tool", "skill", "subagent"]
UnhandledPolicy = Literal["passthrough", "warn", "error"]
SequenceExhaustion = Literal["error", "repeat-last", "passthrough"]
MatchDirective: TypeAlias = Literal["name"] | dict[str, list[str]]

StubResult: TypeAlias = Any | Callable[[Any], Any | Awaitable[Any]]


@dataclass
class Call:
    kind: CallKind
    name: str
    input: Any
    stubbed: bool
    ts: float
    key: str
    output: Any | None = None
    error: Any | None = None


@dataclass
class SequenceStubState:
    name: str
    kind: CallKind
    length: int
    consumed: int
    exhausted: bool


@dataclass
class RecordedError:
    name: str
    message: str


@dataclass
class RecordedEntry:
    name: str
    kind: CallKind | None = None
    input: Any | None = None
    output: Any | None = None
    error: RecordedError | None = None
    match: MatchDirective | None = None


@dataclass
class CassetteState:
    path: str
    entries: list[RecordedEntry]
    matched: list[ResolverInput]
    missed: list[ResolverInput]
    unused: list[RecordedEntry]


@dataclass
class Resolution:
    produce: Callable[[], Any | Awaitable[Any]]
    passthrough: bool = False


@dataclass
class ResolverInput:
    kind: CallKind
    name: str
    input: Any


Resolver: TypeAlias = Callable[[ResolverInput], Resolution | None]
Redactor: TypeAlias = Callable[[Call], Call]

# Stub dict keys match spec / TS: name, kind, args, match, result, sequence, on_sequence_exhausted
Stub: TypeAlias = dict[str, Any]


@dataclass
class AssertionResult:
    pass_: bool
    message: Callable[[], str]


@dataclass
class ExpectedCall:
    name: str
    kind: CallKind | None = None
    input: Any | None = None
    output: Any | None = None
    error: Any | None = None
    stubbed: bool | None = None


@dataclass
class HarnessOptions:
    stubs: list[Stub] | None = None
    resolvers: list[Resolver] | None = None
    on_unhandled: UnhandledPolicy = "passthrough"
    redact: Redactor | None = None
    cassette: str | None = None
