"""LangChain-style tool adapter — integration guide."""

from __future__ import annotations

from mockist import create_harness
from mockist.adapters.langchain import wrap_langchain_tools


class SearchTool:
    async def ainvoke(self, input: dict) -> str:
        return "real"


async def demo() -> None:
    harness = create_harness(
        stubs=[{"name": "search", "args": {"q": "billing"}, "result": "stub"}],
        on_unhandled="error",
    )
    tool = SearchTool()
    wrapped = wrap_langchain_tools({"search": tool}, harness)
    out = await wrapped["search"].ainvoke({"q": "billing"})
    assert out == "stub"
