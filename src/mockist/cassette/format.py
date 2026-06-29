"""Cassette format v1."""

from __future__ import annotations

import json
from typing import Any

from mockist.cassette.paths import find_redacted_paths
from mockist.types import Call, RecordedEntry, RecordedError

CASSETTE_FORMAT_VERSION = 1


def parse_cassette(text: str, path: str) -> list[RecordedEntry]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f'mockist: cassette "{path}" is not valid JSON: {exc}') from exc

    version = data.get("mockist_format_version")
    if version != CASSETTE_FORMAT_VERSION:
        raise ValueError(
            f'mockist: cassette "{path}" has unsupported mockist_format_version {version} '
            f"(expected {CASSETTE_FORMAT_VERSION})"
        )
    calls = data.get("calls")
    if not isinstance(calls, list):
        raise ValueError(f'mockist: cassette "{path}" is missing a "calls" array')

    entries: list[RecordedEntry] = []
    for i, raw in enumerate(calls):
        entry = _parse_entry(raw, path, i)
        entries.append(entry)
    return entries


def _parse_entry(raw: dict[str, Any], path: str, index: int) -> RecordedEntry:
    name = raw.get("name", "")
    has_output = "output" in raw
    has_error = "error" in raw
    if has_output == has_error:
        raise ValueError(
            f'mockist: cassette "{path}" call [{index}] ("{name}") must define exactly one of "output" or "error"'
        )
    error = None
    if has_error:
        err = raw["error"]
        if not isinstance(err, dict) or not isinstance(err.get("message"), str):
            raise ValueError(
                f'mockist: cassette "{path}" call [{index}] ("{name}") has an invalid "error" object'
            )
        error = RecordedError(name=str(err.get("name", "Error")), message=err["message"])
    match = raw.get("match")
    if match is not None and match != "name":
        if not isinstance(match, dict) or not isinstance(match.get("ignore"), list):
            raise ValueError(
                f'mockist: cassette "{path}" call [{index}] ("{name}") has an invalid "match" directive'
            )
    return RecordedEntry(
        name=name,
        kind=raw.get("kind"),
        input=raw.get("input"),
        output=raw.get("output") if has_output else None,
        error=error,
        match=match,
    )


def serialize_cassette(calls: list[Call], *, now: str) -> str:
    entries = [_to_entry(call, i) for i, call in enumerate(calls)]
    redactions = [
        path
        for i, entry in enumerate(entries)
        for path in (
            find_redacted_paths(entry.input, f"calls[{i}].input")
            + find_redacted_paths(entry.output, f"calls[{i}].output")
        )
    ]
    file: dict[str, Any] = {
        "mockist_format_version": CASSETTE_FORMAT_VERSION,
        "recordedAt": now,
        "redactions": redactions,
        "calls": [_entry_to_dict(entry) for entry in entries],
    }
    return json.dumps(_sort_keys(file), indent=2)


def _to_entry(call: Call, index: int) -> RecordedEntry:
    _assert_serializable(call.input, f"calls[{index}].input")
    entry = RecordedEntry(name=call.name, input=call.input)
    if call.kind != "tool":
        entry.kind = call.kind
    if call.error is not None:
        if isinstance(call.error, BaseException):
            entry.error = RecordedError(name=type(call.error).__name__, message=str(call.error))
        else:
            entry.error = RecordedError(name="Error", message=str(call.error))
    else:
        _assert_serializable(call.output, f"calls[{index}].output")
        entry.output = call.output
    return entry


def _entry_to_dict(entry: RecordedEntry) -> dict[str, Any]:
    out: dict[str, Any] = {"name": entry.name}
    if entry.kind is not None and entry.kind != "tool":
        out["kind"] = entry.kind
    if entry.input is not None:
        out["input"] = entry.input
    if entry.error is not None:
        out["error"] = {"name": entry.error.name, "message": entry.error.message}
    else:
        out["output"] = entry.output
    if entry.match is not None:
        out["match"] = entry.match
    return out


def _assert_serializable(value: Any, where: str, seen: set[int] | None = None) -> None:
    if value is None or isinstance(value, (str, int, float, bool)):
        return
    if callable(value):
        raise ValueError(
            f"mockist: cannot serialize function at {where} — cassette values must be JSON-serializable"
        )
    if seen is None:
        seen = set()
    obj_id = id(value)
    if obj_id in seen:
        raise ValueError(
            f"mockist: cannot serialize circular reference at {where} — cassette values must be JSON-serializable"
        )
    seen.add(obj_id)
    if isinstance(value, list):
        for i, item in enumerate(value):
            _assert_serializable(item, f"{where}[{i}]", seen)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            _assert_serializable(item, f"{where}.{key}", seen)


def _sort_keys(value: Any) -> Any:
    if isinstance(value, list):
        return [_sort_keys(item) for item in value]
    if isinstance(value, dict):
        return {k: _sort_keys(value[k]) for k in sorted(value.keys(), key=str)}
    return value
