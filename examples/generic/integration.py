"""Generic callable adapter — integration guide (M0).

Copy this pattern into your app once ``create_harness`` and ``wrap_tools`` land.

Steps:
    1. Declare boundary stubs on a harness.
    2. Wrap your tool map with ``wrap_tools``.
    3. Pass wrapped tools to your agent entry point.
    4. Assert ``harness.trajectory`` (or pytest helpers).

This module is documentation-as-code. It imports only what exists today so CI can
load it before M0 ships.
"""

from __future__ import annotations

import mockist

# --- Target wiring (uncomment when M0 is implemented) ---
#
# from mockist import create_harness, expect_called_with, wrap_tools
#
# async def get_weather(input: dict) -> dict:
#     return {"city": input["city"], "temp_c": 18}
#
# harness = create_harness(
#     on_unhandled="error",
#     stubs=[
#         {
#             "name": "get_weather",
#             "args": {"city": "Paris"},
#             "result": {"city": "Paris", "temp_c": 21},
#         },
#     ],
# )
#
# tools = wrap_tools({"get_weather": get_weather}, harness)
# result = await run_agent(prompt="What's the weather in Paris?", tools=tools)
# assert expect_called_with(harness.trajectory, "get_weather", {"city": "Paris"}).pass_

GUIDE_VERSION = mockist.__version__

TARGET_APIS = (
    "create_harness",
    "wrap_tools",
    "expect_called_with",
)
