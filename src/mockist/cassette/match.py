"""Cassette input matching."""

from __future__ import annotations

from typing import Any

from mockist.cassette.paths import blank_paths, find_redacted_paths
from mockist.deep_equal import deep_equal
from mockist.types import RecordedEntry


def input_matches(entry: RecordedEntry, input: Any) -> bool:
    if entry.match == "name":
        return True
    explicit: list[str] = []
    if isinstance(entry.match, dict) and isinstance(entry.match.get("ignore"), list):
        explicit = list(entry.match["ignore"])
    ignore = explicit + find_redacted_paths(entry.input, "input")
    a = blank_paths({"input": entry.input}, ignore)
    b = blank_paths({"input": input}, ignore)
    return deep_equal(a, b)
