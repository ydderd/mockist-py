"""LangChain-style tool adapter."""

from __future__ import annotations

from typing import Any, TypeVar

from mockist.harness import Harness

T = TypeVar("T", bound=dict[str, Any])


def wrap_langchain_tools(tools: T, harness: Harness) -> T:
    wrapped: dict[str, Any] = {}
    for name, tool in tools.items():
        wrapped[name] = _wrap_langchain_tool(name, tool, harness)
    return wrapped  # type: ignore[return-value]


def _wrap_langchain_tool(name: str, tool: Any, harness: Harness) -> Any:
    if hasattr(tool, "ainvoke") and callable(tool.ainvoke):
        original = tool.ainvoke

        async def ainvoke(input: Any, *args: Any, **kwargs: Any) -> Any:
            normalized = _normalize_input(input)
            return await harness.dispatch(
                "tool",
                name,
                normalized,
                lambda: original(input, *args, **kwargs),
            )

        tool.ainvoke = ainvoke
        return tool

    if hasattr(tool, "invoke") and callable(tool.invoke):
        original = tool.invoke

        async def invoke(input: Any, *args: Any, **kwargs: Any) -> Any:
            normalized = _normalize_input(input)
            return await harness.dispatch(
                "tool",
                name,
                normalized,
                lambda: original(input, *args, **kwargs),
            )

        tool.invoke = invoke
        return tool

    if callable(tool):
        async def call(input: Any, *args: Any, **kwargs: Any) -> Any:
            normalized = _normalize_input(input)
            return await harness.dispatch(
                "tool",
                name,
                normalized,
                lambda: tool(input, *args, **kwargs),
            )

        return call

    return tool


def _normalize_input(input: Any) -> Any:
    if isinstance(input, dict):
        return input
    return {"input": input}
