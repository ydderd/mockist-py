"""CI guard for examples/langchain/integration.py."""

from __future__ import annotations

import asyncio

from examples.langchain import integration as langchain_integration


def test_integration_runs() -> None:
    asyncio.run(langchain_integration.demo())
