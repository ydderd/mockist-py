"""Optional pytest integration."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

import pytest

from mockist.assertions import (
    expect_called_tool,
    expect_called_with,
    expect_cassette_fully_used,
    expect_exact_trajectory,
    expect_no_exhausted_sequences,
    expect_no_passthrough_calls,
    expect_subsequence,
)
from mockist.cassette.registry import flush_pending_saves
from mockist.harness import Harness


class MockistAssert:
    def called_tool(self, harness: Harness, name: str) -> None:
        result = expect_called_tool(harness.trajectory, name)
        if not result.pass_:
            pytest.fail(result.message())

    def called_with(self, harness: Harness, name: str, partial_input: object) -> None:
        result = expect_called_with(harness.trajectory, name, partial_input)
        if not result.pass_:
            pytest.fail(result.message())

    def exact_trajectory(self, harness: Harness, expected: list[dict[str, Any]]) -> None:
        result = expect_exact_trajectory(harness.trajectory, expected)
        if not result.pass_:
            pytest.fail(result.message())

    def subsequence(self, harness: Harness, expected: list[dict[str, Any]]) -> None:
        result = expect_subsequence(harness.trajectory, expected)
        if not result.pass_:
            pytest.fail(result.message())

    def no_passthrough(self, harness: Harness) -> None:
        result = expect_no_passthrough_calls(harness.trajectory)
        if not result.pass_:
            pytest.fail(result.message())

    def no_exhausted_sequences(self, harness: Harness) -> None:
        result = expect_no_exhausted_sequences(harness.sequence_state())
        if not result.pass_:
            pytest.fail(result.message())

    def cassette_fully_used(self, harness: Harness) -> None:
        result = expect_cassette_fully_used(harness.cassette_state())
        if not result.pass_:
            pytest.fail(result.message())


@pytest.fixture
def mockist_assert() -> MockistAssert:
    return MockistAssert()


@pytest.fixture(autouse=True)
async def _flush_mockist_cassette_saves() -> AsyncGenerator[None, None]:
    yield
    await flush_pending_saves()


def pytest_configure(config: object) -> None:
    """Register the mockist pytest plugin."""
