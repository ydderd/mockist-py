"""CI guard for examples/openai/integration.py."""

from __future__ import annotations

import asyncio

from examples.openai import integration as openai_integration


def test_integration_runs() -> None:
    asyncio.run(openai_integration.demo())
