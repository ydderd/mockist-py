"""In-memory trajectory recorder."""

from __future__ import annotations

from mockist.types import Call, Redactor


class Recorder:
    def __init__(self, redact: Redactor | None = None) -> None:
        self._calls: list[Call] = []
        self._redact = redact or (lambda call: call)

    def record(self, call: Call) -> None:
        self._calls.append(self._redact(call))

    @property
    def trajectory(self) -> list[Call]:
        return list(self._calls)

    def reset(self) -> None:
        self._calls.clear()
