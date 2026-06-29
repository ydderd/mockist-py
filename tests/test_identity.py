"""Identity and deep_equal tests."""

from __future__ import annotations

from mockist.deep_equal import deep_equal
from mockist.identity import identify, stable_stringify


def test_stable_stringify_sorts_keys() -> None:
    assert stable_stringify({"b": 1, "a": 2}) == stable_stringify({"a": 2, "b": 1})


def test_deep_equal_uses_stable_stringify() -> None:
    assert deep_equal({"a": 1}, {"a": 1})


def test_identify_includes_kind_name_input() -> None:
    key = identify("tool", "w", {"city": "Paris"})
    assert key.startswith("tool:w:")
