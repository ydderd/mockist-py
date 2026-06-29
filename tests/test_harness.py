"""Harness tests."""

from __future__ import annotations

import pytest

from mockist import create_harness


@pytest.mark.asyncio
async def test_stub_hit_returns_value_and_never_calls_original() -> None:
    harness = create_harness(stubs=[{"name": "w", "args": {"city": "Paris"}, "result": {"temp_c": 21}}])
    called = False

    async def original() -> dict:
        nonlocal called
        called = True
        return {"temp_c": 99}

    out = await harness.dispatch("tool", "w", {"city": "Paris"}, original)
    assert out == {"temp_c": 21}
    assert not called
    assert harness.trajectory[0].stubbed is True
    assert harness.trajectory[0].output == {"temp_c": 21}


@pytest.mark.asyncio
async def test_miss_passthrough_records_stubbed_false() -> None:
    harness = create_harness(stubs=[{"name": "w", "args": {"city": "Paris"}, "result": 1}])
    calls = 0

    async def original() -> dict:
        nonlocal calls
        calls += 1
        return {"temp_c": 99}

    out = await harness.dispatch("tool", "w", {"city": "Berlin"}, original)
    assert out == {"temp_c": 99}
    assert calls == 1
    assert harness.trajectory[0].stubbed is False


@pytest.mark.asyncio
async def test_throwing_stub_recorded_and_reraised() -> None:
    def raise_503(_input: object) -> None:
        raise RuntimeError("503")

    harness = create_harness(stubs=[{"name": "flaky", "result": raise_503}])

    async def original() -> str:
        return "real"

    with pytest.raises(RuntimeError, match="503"):
        await harness.dispatch("tool", "flaky", {}, original)
    assert harness.trajectory[0].stubbed is True
    assert isinstance(harness.trajectory[0].error, RuntimeError)


@pytest.mark.asyncio
async def test_unhandled_error_raises() -> None:
    harness = create_harness(on_unhandled="error")
    with pytest.raises(Exception, match="unhandled"):
        await harness.dispatch("tool", "missing", {}, lambda: "x")


@pytest.mark.asyncio
async def test_predicate_stub_matches() -> None:
    harness = create_harness(
        stubs=[{"name": "search", "match": lambda i: "docs" in i["q"], "result": {"hits": []}}]
    )
    out = await harness.dispatch("tool", "search", {"q": "docs billing"}, lambda: {"hits": ["x"]})
    assert out == {"hits": []}


@pytest.mark.asyncio
async def test_reset_clears_trajectory() -> None:
    harness = create_harness(stubs=[{"name": "w", "result": 1}])
    await harness.dispatch("tool", "w", {}, lambda: 2)
    harness.reset()
    assert harness.trajectory == []
