"""Structural equality."""

from __future__ import annotations

from typing import Any

from mockist.identity import stable_stringify


def deep_equal(a: Any, b: Any) -> bool:
    return stable_stringify(a) == stable_stringify(b)
