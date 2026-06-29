"""Assertion helper tests."""

from __future__ import annotations

from mockist import (
    expect_called_tool,
    expect_called_with,
    expect_exact_trajectory,
    expect_no_passthrough_calls,
    expect_subsequence,
)
from mockist.types import Call


def _call(name: str, **kwargs) -> Call:
    return Call(
        kind="tool",
        name=name,
        input=kwargs.get("input", {}),
        output=kwargs.get("output"),
        error=kwargs.get("error"),
        stubbed=kwargs.get("stubbed", True),
        ts=1.0,
        key="k",
    )


def test_expect_exact_trajectory_passes() -> None:
    trajectory = [_call("w", input={"city": "Paris"}, output={"temp_c": 21})]
    result = expect_exact_trajectory(
        trajectory,
        [{"name": "w", "input": {"city": "Paris"}, "stubbed": True}],
    )
    assert result.pass_


def test_expect_called_with_partial_input() -> None:
    trajectory = [_call("w", input={"city": "Paris", "units": "c"})]
    result = expect_called_with(trajectory, "w", {"city": "Paris"})
    assert result.pass_


def test_expect_subsequence_allows_gaps() -> None:
    trajectory = [
        _call("a"),
        _call("b"),
        _call("c"),
    ]
    result = expect_subsequence(trajectory, [{"name": "a"}, {"name": "c"}])
    assert result.pass_


def test_expect_no_passthrough_calls() -> None:
    trajectory = [_call("w", stubbed=False)]
    result = expect_no_passthrough_calls(trajectory)
    assert not result.pass_


def test_expect_called_tool() -> None:
    assert expect_called_tool([_call("w")], "w").pass_
    assert not expect_called_tool([_call("x")], "w").pass_
