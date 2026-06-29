"""mockist — local test harness for agent tool/skill boundaries."""

from importlib.metadata import PackageNotFoundError, version

from mockist.adapters.generic import wrap_tools
from mockist.assertions import (
    cassette_expected_calls,
    expect_called_tool,
    expect_called_with,
    expect_cassette_fully_used,
    expect_exact_trajectory,
    expect_no_exhausted_sequences,
    expect_no_passthrough_calls,
    expect_no_unhandled_calls,
    expect_subsequence,
)
from mockist.composition import concat_trajectories, merge_harness_trajectories
from mockist.harness import Harness, create_harness
from mockist.registry import define_stubs

try:
    __version__ = version("mockist")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = [
    "Harness",
    "cassette_expected_calls",
    "concat_trajectories",
    "create_harness",
    "define_stubs",
    "expect_called_tool",
    "expect_called_with",
    "expect_cassette_fully_used",
    "expect_exact_trajectory",
    "expect_no_exhausted_sequences",
    "expect_no_passthrough_calls",
    "expect_no_unhandled_calls",
    "expect_subsequence",
    "merge_harness_trajectories",
    "wrap_tools",
    "__version__",
]
