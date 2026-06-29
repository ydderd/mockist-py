"""Generic callable adapter — integration guide."""

from __future__ import annotations

from mockist import create_harness, expect_called_with, wrap_tools


async def get_weather(input: dict) -> dict:
    return {"city": input["city"], "temp_c": 18}


async def run_agent(*, prompt: str, tools: dict) -> object:
    _ = prompt
    result = await tools["get_weather"]({"city": "Paris"})
    return type("AgentResult", (), {"text": f"Temperature is {result['temp_c']}C"})()


async def demo() -> None:
    harness = create_harness(
        on_unhandled="error",
        stubs=[
            {
                "name": "get_weather",
                "args": {"city": "Paris"},
                "result": {"city": "Paris", "temp_c": 21},
            },
        ],
    )
    tools = wrap_tools({"get_weather": get_weather}, harness)
    result = await run_agent(prompt="What's the weather in Paris?", tools=tools)
    assert "21" in result.text
    assert expect_called_with(harness.trajectory, "get_weather", {"city": "Paris"}).pass_
