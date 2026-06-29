"""OpenAI adapter tests."""

from __future__ import annotations

import pytest

from mockist import create_harness
from mockist.adapters.openai import create_openai_tool_interceptor, wrap_openai_tools


@pytest.mark.asyncio
async def test_wrap_openai_tools() -> None:
    harness = create_harness(stubs=[{"name": "w", "args": {"city": "Paris"}, "result": 21}])
    calls = 0

    async def execute(input: dict) -> int:
        nonlocal calls
        calls += 1
        return 99

    tools = wrap_openai_tools({"w": {"execute": execute}}, harness)
    out = await tools["w"]["execute"]({"city": "Paris"})
    assert out == 21
    assert calls == 0


@pytest.mark.asyncio
async def test_openai_interceptor() -> None:
    harness = create_harness(stubs=[{"name": "w", "result": "stub"}])
    calls = 0

    async def run_tool(name: str, args: object) -> str:
        nonlocal calls
        calls += 1
        return "real"

    intercept = create_openai_tool_interceptor(harness, run_tool)
    assert await intercept("w", {}) == "stub"
    assert calls == 0
