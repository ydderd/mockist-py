"""OpenAI-style tool adapter."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from mockist.harness import Harness

T = TypeVar("T", bound=dict[str, Any])


def wrap_openai_tools(tools: T, harness: Harness) -> T:
    wrapped: dict[str, Any] = {}
    for name, tool in tools.items():
        execute = tool.get("execute") if isinstance(tool, dict) else getattr(tool, "execute", None)
        if not callable(execute):
            wrapped[name] = tool
            continue
        if isinstance(tool, dict):
            new_tool = dict(tool)
            exec_fn = execute

            async def wrapped_execute(input: Any, name=name, exec_fn=exec_fn) -> Any:
                return await harness.dispatch(
                    "tool",
                    name,
                    input,
                    lambda: exec_fn(input),
                )

            new_tool["execute"] = wrapped_execute
            wrapped[name] = new_tool
        else:
            original = execute.__get__(tool, type(tool))

            async def wrapped_object_execute(input: Any, name=name, original=original) -> Any:
                return await harness.dispatch(
                    "tool",
                    name,
                    input,
                    lambda: original(input),
                )

            tool.execute = wrapped_object_execute
            wrapped[name] = tool
    return wrapped  # type: ignore[return-value]


def create_openai_tool_interceptor(
    harness: Harness,
    run_tool: Callable[[str, Any], Awaitable[Any]],
) -> Callable[[str, Any], Awaitable[Any]]:
    async def intercept(name: str, args: Any) -> Any:
        return await harness.dispatch("tool", name, args, lambda: run_tool(name, args))

    return intercept
