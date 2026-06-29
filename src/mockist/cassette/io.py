"""Cassette file I/O."""

from __future__ import annotations

import warnings
from pathlib import Path

from mockist.cassette.format import parse_cassette, serialize_cassette
from mockist.types import Call, RecordedEntry

_missing_warned: set[str] = set()


def load_cassette_entries(path: str) -> list[RecordedEntry]:
    file_path = Path(path)
    if not file_path.exists():
        if path not in _missing_warned:
            _missing_warned.add(path)
            warnings.warn(
                f'mockist: cassette "{path}" not found — no recorded calls loaded '
                f"(all calls use the on_unhandled policy).",
                stacklevel=2,
            )
        return []
    text = file_path.read_text(encoding="utf-8")
    return parse_cassette(text, path)


def write_cassette(path: str, calls: list[Call], *, now: str) -> None:
    text = serialize_cassette(calls, now=now)
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(text + "\n", encoding="utf-8")
