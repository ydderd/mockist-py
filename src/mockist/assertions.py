"""Trajectory assertions."""

from __future__ import annotations

import json
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from mockist.deep_equal import deep_equal
from mockist.types import (
    AssertionResult,
    Call,
    CassetteState,
    ExpectedCall,
    SequenceStubState,
)

if TYPE_CHECKING:
    from mockist.harness import Harness


def _format_value(value: Any) -> str:
    if isinstance(value, BaseException):
        return f"Error({json.dumps(str(value))})"
    if value is None:
        return "null"
    try:
        return json.dumps(value)
    except (TypeError, ValueError):
        return str(value)


def _describe_call(call: Call, index: int) -> str:
    parts = [f"{call.kind} {call.name}", f"input={_format_value(call.input)}"]
    if call.error is not None:
        parts.append(f"error={_format_value(call.error)}")
    else:
        parts.append(f"output={_format_value(call.output)}")
    parts.append("stubbed" if call.stubbed else "passthrough")
    return f"  [{index}] {' '.join(parts)}"


def _describe_expected(expected: ExpectedCall, index: int) -> str:
    parts = [f"{expected.kind or 'tool'} {expected.name}"]
    if expected.input is not None:
        parts.append(f"input={_format_value(expected.input)}")
    if expected.error is not None:
        parts.append(f"error={_format_value(expected.error)}")
    if expected.output is not None:
        parts.append(f"output={_format_value(expected.output)}")
    if expected.stubbed is not None:
        parts.append("stubbed" if expected.stubbed else "passthrough")
    return f"  [{index}] {' '.join(parts)}"


def _render_trajectory(trajectory: list[Call]) -> str:
    if not trajectory:
        return "Actual trajectory: (no calls recorded)"
    return "Actual trajectory:\n" + "\n".join(_describe_call(c, i) for i, c in enumerate(trajectory))


def _render_expected(expected: list[ExpectedCall]) -> str:
    if not expected:
        return "Expected trajectory: (no calls)"
    return "Expected trajectory:\n" + "\n".join(_describe_expected(e, i) for i, e in enumerate(expected))


def _diff_block(expected: list[ExpectedCall], trajectory: list[Call], reason: str) -> str:
    return "\n".join([reason, _render_expected(expected), _render_trajectory(trajectory)])


def _deep_subset(subset: Any, actual: Any) -> bool:
    if subset is None or not isinstance(subset, (dict, list)):
        return deep_equal(subset, actual)
    if actual is None or not isinstance(actual, (dict, list)):
        return False
    if isinstance(subset, list):
        if not isinstance(actual, list) or len(subset) != len(actual):
            return False
        return all(_deep_subset(s, actual[i]) for i, s in enumerate(subset))
    if isinstance(actual, list):
        return False
    return all(k in actual and _deep_subset(subset[k], actual[k]) for k in subset)


def _call_matches(call: Call, expected: ExpectedCall) -> bool:
    if call.name != expected.name:
        return False
    if expected.kind is not None and call.kind != expected.kind:
        return False
    if expected.input is not None and not deep_equal(call.input, expected.input):
        return False
    if expected.output is not None and not deep_equal(call.output, expected.output):
        return False
    if expected.error is not None and not deep_equal(call.error, expected.error):
        return False
    if expected.stubbed is not None and call.stubbed != expected.stubbed:
        return False
    return True


def _expected_from_dict(spec: dict[str, Any]) -> ExpectedCall:
    return ExpectedCall(
        name=spec["name"],
        kind=spec.get("kind"),
        input=spec.get("input"),
        output=spec.get("output"),
        error=spec.get("error"),
        stubbed=spec.get("stubbed"),
    )


def expect_exact_trajectory(
    trajectory: list[Call],
    expected: Sequence[ExpectedCall | dict[str, Any]],
) -> AssertionResult:
    specs = [e if isinstance(e, ExpectedCall) else _expected_from_dict(e) for e in expected]
    if len(trajectory) != len(specs):
        return AssertionResult(
            pass_=False,
            message=lambda: _diff_block(
                specs,
                trajectory,
                f"Expected an exact trajectory of {len(specs)} call(s), but recorded {len(trajectory)}.",
            ),
        )
    for i, spec in enumerate(specs):
        if not _call_matches(trajectory[i], spec):
            return AssertionResult(
                pass_=False,
                message=lambda i=i: _diff_block(specs, trajectory, f"Trajectory mismatch at index {i}."),
            )
    return AssertionResult(pass_=True, message=lambda: f"Trajectory matched {len(specs)} call(s).")


def expect_subsequence(
    trajectory: list[Call],
    expected: Sequence[ExpectedCall | dict[str, Any]],
) -> AssertionResult:
    specs = [e if isinstance(e, ExpectedCall) else _expected_from_dict(e) for e in expected]
    cursor = 0
    for spec in specs:
        while cursor < len(trajectory) and not _call_matches(trajectory[cursor], spec):
            cursor += 1
        if cursor >= len(trajectory):
            return AssertionResult(
                pass_=False,
                message=lambda spec=spec: _diff_block(
                    specs,
                    trajectory,
                    f'Expected calls as an ordered subsequence, but "{spec.name}" was not found in order.',
                ),
            )
        cursor += 1
    return AssertionResult(
        pass_=True,
        message=lambda: f"Found {len(specs)} call(s) as an ordered subsequence.",
    )


def expect_called_tool(trajectory: list[Call], name: str) -> AssertionResult:
    found = any(c.name == name for c in trajectory)
    return AssertionResult(
        pass_=found,
        message=lambda: (
            f'Found call(s) to "{name}".'
            if found
            else f'Expected a call to tool "{name}", but it was never called. Calls recorded: '
            f"{', '.join(c.name for c in trajectory) or '(none)'}."
        ),
    )


def expect_called_with(trajectory: list[Call], name: str, partial_input: Any) -> AssertionResult:
    to_name = [c for c in trajectory if c.name == name]
    found = any(_deep_subset(partial_input, c.input) for c in to_name)
    return AssertionResult(
        pass_=found,
        message=lambda: (
            f'Found a call to "{name}" matching {_format_value(partial_input)}.'
            if found
            else (
                (
                    f'Expected a call to "{name}" with input matching '
                    f"{_format_value(partial_input)}, but \"{name}\" was never called."
                )
                if not to_name
                else "\n".join(
                    [
                        (
                            f'Expected a call to "{name}" with input matching '
                            f"{_format_value(partial_input)}, but none matched."
                        ),
                        f'Calls to "{name}":',
                        *(_describe_call(c, i) for i, c in enumerate(to_name)),
                    ]
                )
            )
        ),
    )


def expect_no_unhandled_calls(trajectory: list[Call]) -> AssertionResult:
    offenders = [c for c in trajectory if not c.stubbed]
    return AssertionResult(
        pass_=len(offenders) == 0,
        message=lambda: (
            "Expected no unhandled (passthrough/error) calls."
            if not offenders
            else "Unhandled calls:\n" + "\n".join(_describe_call(c, i) for i, c in enumerate(offenders))
        ),
    )


def expect_no_passthrough_calls(trajectory: list[Call]) -> AssertionResult:
    return expect_no_unhandled_calls(trajectory)


def expect_no_exhausted_sequences(states: list[SequenceStubState]) -> AssertionResult:
    exhausted = [s for s in states if s.exhausted]
    return AssertionResult(
        pass_=len(exhausted) == 0,
        message=lambda: (
            "Expected no exhausted sequences."
            if not exhausted
            else "Expected no exhausted sequences, but "
            + str(len(exhausted))
            + " ran dry:\n"
            + "\n".join(
                f'  {s.kind} "{s.name}" ({s.length} step(s), all consumed then called again)'
                for s in exhausted
            )
        ),
    )


def _describe_input(call: Any, index: int) -> str:
    return f"  [{index}] {call.kind} {call.name} input={_format_value(call.input)}"


def _describe_entry(entry: Any, index: int) -> str:
    kind = entry.kind or "tool"
    body = (
        f"error={_format_value(entry.error)}"
        if entry.error is not None
        else f"output={_format_value(entry.output)}"
    )
    return f"  [{index}] {kind} {entry.name} input={_format_value(entry.input)} {body}"


def expect_cassette_fully_used(state: CassetteState) -> AssertionResult:
    ok = len(state.missed) == 0 and len(state.unused) == 0
    return AssertionResult(
        pass_=ok,
        message=lambda: (
            f'Cassette "{state.path}" fully used: every entry consumed, no misses.'
            if ok
            else "\n".join(
                [
                    f'Cassette "{state.path}" not fully used.',
                    *(
                        [
                            f"Missed entries ({len(state.missed)}):",
                            *(_describe_input(c, i) for i, c in enumerate(state.missed)),
                        ]
                        if state.missed
                        else []
                    ),
                    *(
                        [
                            f"Unused entries ({len(state.unused)}):",
                            *(_describe_entry(e, i) for i, e in enumerate(state.unused)),
                        ]
                        if state.unused
                        else []
                    ),
                ]
            )
        ),
    )


def cassette_expected_calls(harness: Harness) -> list[ExpectedCall]:
    specs: list[ExpectedCall] = []
    for entry in harness.cassette_state().entries:
        spec = ExpectedCall(name=entry.name)
        if entry.kind is not None:
            spec.kind = entry.kind
        specs.append(spec)
    return specs
