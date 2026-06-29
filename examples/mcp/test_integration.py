"""CI guard for examples/mcp/integration.py."""

from __future__ import annotations

import asyncio

from examples.mcp import integration as mcp_integration


def test_integration_runs() -> None:
    asyncio.run(mcp_integration.demo())
