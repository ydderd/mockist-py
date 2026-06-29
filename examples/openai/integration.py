"""OpenAI-style tool adapter — integration guide."""

from __future__ import annotations

from mockist import create_harness
from mockist.adapters.openai import wrap_openai_tools


async def demo() -> None:
    harness = create_harness(
        stubs=[{"name": "w", "args": {"city": "Paris"}, "result": {"temp_c": 21}}],
        on_unhandled="error",
    )

    async def execute(input: dict) -> dict:
        return {"temp_c": 99}

    tools = wrap_openai_tools({"w": {"execute": execute}}, harness)
    out = await tools["w"]["execute"]({"city": "Paris"})
    assert out == {"temp_c": 21}
