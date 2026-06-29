"""Optional pytest integration (stub until M1)."""

from __future__ import annotations


def pytest_configure(config: object) -> None:
    """Register the mockist pytest plugin."""
