"""Stable call identity."""

from __future__ import annotations

import json
import math
from typing import Any

from mockist.types import CallKind


def stable_stringify(value: Any) -> str:
    if value is None:
        return "null"
    if value is ...:
        return "undefined"
    if isinstance(value, float) and math.isnan(value):
        return "NaN"
    if isinstance(value, BaseException):
        payload = json.dumps({"name": type(value).__name__, "message": str(value)})
        return f"Error:{payload}"
    if isinstance(value, (str, int, float, bool)):
        return json.dumps(value)
    if isinstance(value, list):
        return f"[{','.join(stable_stringify(item) for item in value)}]"
    if isinstance(value, dict):
        keys = sorted(value.keys(), key=lambda k: str(k))
        parts = [f"{json.dumps(str(k))}:{stable_stringify(value[k])}" for k in keys]
        return "{" + ",".join(parts) + "}"
    return json.dumps(str(value))


def identify(kind: CallKind, name: str, input: Any) -> str:
    return f"{kind}:{name}:{stable_stringify(input)}"
