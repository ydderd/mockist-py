"""Cassette format and replay tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mockist import create_harness
from mockist.cassette.format import parse_cassette, serialize_cassette
from mockist.cassette.redact import default_redactor
from mockist.types import Call

SPEC_FIXTURE = {
    "mockist_format_version": 1,
    "recordedAt": "2026-06-29T18:04:00Z",
    "redactions": ["calls[0].input.headers.authorization"],
    "calls": [
        {"name": "search", "input": {"q": "billing"}, "output": {"hits": ["doc-1"]}},
        {
            "name": "search",
            "input": {"q": "billing", "requestId": "[REDACTED:requestId]"},
            "error": {"name": "TimeoutError", "message": "upstream timeout"},
            "match": {"ignore": ["input.requestId"]},
        },
        {"name": "now", "output": "2026-06-29T00:00:00Z", "match": "name"},
    ],
}


def test_parse_spec_fixture() -> None:
    entries = parse_cassette(json.dumps(SPEC_FIXTURE), "spec.json")
    assert len(entries) == 3
    assert entries[1].error is not None


@pytest.mark.asyncio
async def test_replay_serves_cassette_without_calling_original(tmp_path: Path) -> None:
    path = tmp_path / "flow.json"
    path.write_text(json.dumps(SPEC_FIXTURE), encoding="utf-8")
    harness = create_harness(cassette=str(path), on_unhandled="error")
    called = False

    async def original() -> str:
        nonlocal called
        called = True
        return "real"

    out = await harness.dispatch("tool", "search", {"q": "billing"}, original)
    assert out == {"hits": ["doc-1"]}
    assert not called


@pytest.mark.asyncio
async def test_record_writes_format_version(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MOCKIST_RECORD", "1")
    path = tmp_path / "rec.json"
    harness = create_harness(cassette=str(path), on_unhandled="error")
    await harness.dispatch("tool", "w", {"city": "Paris"}, lambda: {"temp_c": 18})
    harness.save()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["mockist_format_version"] == 1
    assert data["calls"][0]["name"] == "w"


def test_redactor_scrubs_secrets() -> None:
    call = Call(
        kind="tool",
        name="w",
        input={"authorization": "secret"},
        output={"token": "abc"},
        stubbed=False,
        ts=1.0,
        key="k",
    )
    redacted = default_redactor(call)
    assert redacted.input is not None
    assert redacted.output is not None
    assert redacted.input["authorization"] == "[REDACTED:authorization]"
    assert redacted.output["token"] == "[REDACTED:token]"


def test_malformed_cassette_raises(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text('{"mockist_format_version": 2, "calls": []}', encoding="utf-8")
    with pytest.raises(ValueError, match="unsupported"):
        create_harness(cassette=str(path))


def test_serialize_roundtrip() -> None:
    calls = [
        Call(
            kind="tool",
            name="w",
            input={"city": "Paris"},
            output={"temp_c": 21},
            stubbed=True,
            ts=1.0,
            key="k",
        )
    ]
    text = serialize_cassette(calls, now="2026-06-29T00:00:00Z")
    entries = parse_cassette(text, "mem")
    assert entries[0].name == "w"
