"""Generic callable tool adapter."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from mockist.harness import Harness


def wrap_tools(
    tools: dict[str, Callable[..., Any]], harness: Harness
) -> dict[str, Callable[..., Awaitable[Any]]]:
    return {name: _wrap_one(name, tool, harness) for name, tool in tools.items()}


def _wrap_one(
    name: str, tool: Callable[..., Any], harness: Harness
) -> Callable[..., Awaitable[Any]]:
    async def wrapped(input: Any, *args: Any, **kwargs: Any) -> Any:
        return await harness.dispatch(
            "tool",
            name,
            input,
            lambda: tool(input, *args, **kwargs),
        )

    return wrapped
