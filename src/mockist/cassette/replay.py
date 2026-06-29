"""Cassette replay resolver."""

from __future__ import annotations

from mockist.cassette.match import input_matches
from mockist.types import RecordedEntry, Resolution, ResolverInput


class CassetteResolver:
    def __init__(self, entries: list[RecordedEntry]) -> None:
        self.entries = entries
        self._consumed = [False] * len(entries)
        self._matched: list[ResolverInput] = []
        self._missed: list[ResolverInput] = []

    def reset(self) -> None:
        self._consumed = [False] * len(self.entries)
        self._matched.clear()
        self._missed.clear()

    def state(self) -> dict[str, list]:
        return {
            "matched": list(self._matched),
            "missed": list(self._missed),
            "unused": [entry for i, entry in enumerate(self.entries) if not self._consumed[i]],
        }

    def resolve(self, call: ResolverInput) -> Resolution | None:
        kind, name, input = call.kind, call.name, call.input
        for i, entry in enumerate(self.entries):
            if self._consumed[i]:
                continue
            if (entry.kind or "tool") != kind or entry.name != name:
                continue
            if not input_matches(entry, input):
                continue
            self._consumed[i] = True
            self._matched.append(ResolverInput(kind=kind, name=name, input=input))
            return self._produce(entry)
        self._missed.append(ResolverInput(kind=kind, name=name, input=input))
        return None

    def _produce(self, entry: RecordedEntry) -> Resolution:
        def produce():
            if entry.error is not None:
                exc_type = type(entry.error.name, (Exception,), {})
                raise exc_type(entry.error.message)
            return entry.output

        return Resolution(produce=produce)


def create_cassette_resolver(entries: list[RecordedEntry]) -> CassetteResolver:
    return CassetteResolver(entries)
