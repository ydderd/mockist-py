"""CI guard for examples/generic/integration.py."""

from __future__ import annotations

import asyncio

from examples.generic import integration as generic_integration


def test_integration_runs() -> None:
    asyncio.run(generic_integration.demo())
