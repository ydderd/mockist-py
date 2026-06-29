"""MCP tool adapter."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from mockist.async_utils import await_maybe
from mockist.harness import Harness

McpToolHandler = Callable[[dict[str, Any]], Any | Awaitable[Any]]
McpHandlerMap = dict[str, McpToolHandler]
T = TypeVar("T", bound=McpHandlerMap)


def wrap_mcp_tool_handler(harness: Harness, name: str, handler: McpToolHandler) -> McpToolHandler:
    async def wrapped(args: dict[str, Any]) -> Any:
        async def run() -> Any:
            return await await_maybe(handler(args))

        return await harness.dispatch(
            "tool",
            name,
            args.get("arguments"),
            run,
        )

    return wrapped


def wrap_mcp_handlers(handlers: T, harness: Harness) -> T:
    return {name: wrap_mcp_tool_handler(harness, name, handler) for name, handler in handlers.items()}  # type: ignore[return-value]


def create_mcp_client_interceptor(
    harness: Harness,
    call_tool: Callable[[str, Any], Awaitable[Any]],
) -> Callable[[str, Any], Awaitable[Any]]:
    async def intercept(name: str, args: Any) -> Any:
        return await harness.dispatch("tool", name, args, lambda: call_tool(name, args))

    return intercept
