"""Sequential stub tests."""

from __future__ import annotations

import pytest

from mockist import create_harness


@pytest.mark.asyncio
async def test_sequence_error_then_success() -> None:
    harness = create_harness(
        stubs=[
            {
                "name": "flaky",
                "sequence": [{"error": RuntimeError("503")}, {"result": "ok"}],
            }
        ]
    )

    async def original() -> str:
        return "real"

    with pytest.raises(RuntimeError, match="503"):
        await harness.dispatch("tool", "flaky", {}, original)
    assert await harness.dispatch("tool", "flaky", {}, original) == "ok"
    assert len(harness.trajectory) == 2
    assert harness.trajectory[0].stubbed is True
    assert harness.trajectory[1].output == "ok"


@pytest.mark.asyncio
async def test_exhausted_passthrough_runs_original() -> None:
    harness = create_harness(
        stubs=[
            {
                "name": "eventually-real",
                "sequence": [{"result": "stubbed"}],
                "on_sequence_exhausted": "passthrough",
            }
        ]
    )
    calls = 0

    async def original() -> str:
        nonlocal calls
        calls += 1
        return "real"

    assert await harness.dispatch("tool", "eventually-real", {}, original) == "stubbed"
    assert await harness.dispatch("tool", "eventually-real", {}, original) == "real"
    assert calls == 1
    assert harness.trajectory[1].stubbed is False


@pytest.mark.asyncio
async def test_exhausted_passthrough_bypasses_on_unhandled_error() -> None:
    harness = create_harness(
        on_unhandled="error",
        stubs=[
            {
                "name": "eventually-real",
                "sequence": [{"result": "stubbed"}],
                "on_sequence_exhausted": "passthrough",
            }
        ],
    )
    assert await harness.dispatch("tool", "eventually-real", {}, lambda: "real") == "stubbed"
    assert await harness.dispatch("tool", "eventually-real", {}, lambda: "real") == "real"


def test_sequence_state_tracks_consumption() -> None:
    harness = create_harness(
        stubs=[{"name": "s", "sequence": [{"result": 1}, {"result": 2}]}]
    )
    import asyncio

    asyncio.run(harness.dispatch("tool", "s", {}, lambda: 0))
    state = harness.sequence_state()[0]
    assert state.consumed == 1
    assert state.length == 2
    assert state.exhausted is False
