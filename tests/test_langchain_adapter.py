"""LangChain adapter tests."""

from __future__ import annotations

import pytest

from mockist import create_harness
from mockist.adapters.langchain import wrap_langchain_tools


class FakeTool:
    def __init__(self) -> None:
        self.calls = 0

    async def ainvoke(self, input: dict) -> str:
        self.calls += 1
        return "real"


@pytest.mark.asyncio
async def test_wrap_langchain_ainvoke() -> None:
    harness = create_harness(stubs=[{"name": "search", "args": {"q": "billing"}, "result": "stub"}])
    tool = FakeTool()
    wrapped = wrap_langchain_tools({"search": tool}, harness)
    out = await wrapped["search"].ainvoke({"q": "billing"})
    assert out == "stub"
    assert tool.calls == 0
