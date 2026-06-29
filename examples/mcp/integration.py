"""MCP server handler adapter — integration guide."""

from __future__ import annotations

from mockist import create_harness
from mockist.adapters.mcp import wrap_mcp_handlers


async def demo() -> None:
    harness = create_harness(
        stubs=[{"name": "search", "args": {"q": "billing"}, "result": {"hits": []}}],
        on_unhandled="error",
    )

    async def handler(args: dict) -> dict:
        return {"hits": ["real"]}

    handlers = wrap_mcp_handlers({"search": handler}, harness)
    out = await handlers["search"]({"arguments": {"q": "billing"}})
    assert out == {"hits": []}
