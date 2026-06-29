"""Cross-language cassette fixture replay."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mockist import create_harness, expect_cassette_fully_used

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "cassettes"


@pytest.fixture
def fixtures_dir() -> Path:
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    return FIXTURES_DIR


@pytest.mark.asyncio
async def test_replay_spec_example_fixture(fixtures_dir: Path) -> None:
    path = fixtures_dir / "spec_example.json"
    if not path.exists():
        path.write_text(
            json.dumps(
                {
                    "mockist_format_version": 1,
                    "recordedAt": "2026-06-29T18:04:00Z",
                    "calls": [
                        {
                            "name": "search",
                            "input": {"q": "billing"},
                            "output": {"hits": ["doc-1"]},
                        },
                        {
                            "name": "now",
                            "output": "2026-06-29T00:00:00Z",
                            "match": "name",
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )
    harness = create_harness(cassette=str(path), on_unhandled="error")
    out1 = await harness.dispatch("tool", "search", {"q": "billing"}, lambda: "miss")
    out2 = await harness.dispatch("tool", "now", {"any": "input"}, lambda: "miss")
    assert out1 == {"hits": ["doc-1"]}
    assert out2 == "2026-06-29T00:00:00Z"
    assert expect_cassette_fully_used(harness.cassette_state()).pass_
