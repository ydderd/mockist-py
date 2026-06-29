"""Generic adapter tests."""

from __future__ import annotations

import pytest

from mockist import create_harness, wrap_tools


@pytest.mark.asyncio
async def test_async_callable_wrapper() -> None:
    harness = create_harness(stubs=[{"name": "get_weather", "args": {"city": "Paris"}, "result": {"temp_c": 21}}])
    calls = 0

    async def get_weather(input: dict) -> dict:
        nonlocal calls
        calls += 1
        return {"temp_c": 99}

    tools = wrap_tools({"get_weather": get_weather}, harness)
    out = await tools["get_weather"]({"city": "Paris"})
    assert out == {"temp_c": 21}
    assert calls == 0


@pytest.mark.asyncio
async def test_sync_callable_wrapper() -> None:
    harness = create_harness(stubs=[{"name": "now", "result": "fixed"}])

    def now(_input: dict) -> str:
        return "real"

    tools = wrap_tools({"now": now}, harness)
    out = await tools["now"]({})
    assert out == "fixed"
