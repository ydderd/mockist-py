"""Cross-adapter parity."""

from __future__ import annotations

import pytest

from mockist import create_harness
from mockist.adapters.generic import wrap_tools
from mockist.adapters.mcp import wrap_mcp_handlers
from mockist.adapters.openai import wrap_openai_tools


@pytest.mark.asyncio
async def test_stub_hit_never_calls_original_across_adapters() -> None:
    harness = create_harness(stubs=[{"name": "w", "args": {"x": 1}, "result": "stub"}])

    async def generic_fn(input: dict) -> str:
        raise AssertionError("should not run")

    generic = wrap_tools({"w": generic_fn}, harness)
    assert await generic["w"]({"x": 1}) == "stub"

    harness.reset()
    harness = create_harness(stubs=[{"name": "w", "args": {"x": 1}, "result": "stub"}])

    async def execute(input: dict) -> str:
        raise AssertionError("should not run")

    openai = wrap_openai_tools({"w": {"execute": execute}}, harness)
    assert await openai["w"]["execute"]({"x": 1}) == "stub"

    harness.reset()
    harness = create_harness(stubs=[{"name": "w", "args": {"x": 1}, "result": "stub"}])

    async def handler(args: dict) -> str:
        raise AssertionError("should not run")

    mcp = wrap_mcp_handlers({"w": handler}, harness)
    assert await mcp["w"]({"arguments": {"x": 1}}) == "stub"
