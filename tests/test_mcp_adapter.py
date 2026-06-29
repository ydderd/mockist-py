"""MCP adapter tests."""

from __future__ import annotations

import pytest

from mockist import create_harness
from mockist.adapters.mcp import create_mcp_client_interceptor, wrap_mcp_handlers


@pytest.mark.asyncio
async def test_wrap_mcp_handlers() -> None:
    harness = create_harness(stubs=[{"name": "search", "args": {"q": "billing"}, "result": {"hits": []}}])
    calls = 0

    async def handler(args: dict) -> dict:
        nonlocal calls
        calls += 1
        return {"hits": ["real"]}

    handlers = wrap_mcp_handlers({"search": handler}, harness)
    out = await handlers["search"]({"arguments": {"q": "billing"}})
    assert out == {"hits": []}
    assert calls == 0


@pytest.mark.asyncio
async def test_mcp_client_interceptor() -> None:
    harness = create_harness(stubs=[{"name": "search", "result": "stub"}])

    async def call_tool(name: str, args: object) -> str:
        return "real"

    intercept = create_mcp_client_interceptor(harness, call_tool)
    assert await intercept("search", {"q": "x"}) == "stub"
