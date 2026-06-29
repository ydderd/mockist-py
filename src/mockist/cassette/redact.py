"""Cassette redaction."""

from __future__ import annotations

import copy
import re
from typing import Any

from mockist.types import Call

SECRET_KEYS = {
    "authorization",
    "api_key",
    "apikey",
    "token",
    "password",
    "secret",
    "cookie",
    "set-cookie",
}

REDACTED_RE = re.compile(r"^\[REDACTED(?::[^\]]*)?\]$")


def redaction_sentinel(key: str) -> str:
    return f"[REDACTED:{key}]"


def is_redacted(value: Any) -> bool:
    return isinstance(value, str) and bool(REDACTED_RE.match(value))


def _scrub(value: Any) -> Any:
    if isinstance(value, list):
        return [_scrub(item) for item in value]
    if isinstance(value, dict):
        return {
            key: redaction_sentinel(key) if key.lower() in SECRET_KEYS else _scrub(item)
            for key, item in value.items()
        }
    return value


def default_redactor(call: Call) -> Call:
    return Call(
        kind=call.kind,
        name=call.name,
        input=_scrub(copy.deepcopy(call.input)),
        output=_scrub(copy.deepcopy(call.output)) if call.output is not None else call.output,
        error=call.error,
        stubbed=call.stubbed,
        ts=call.ts,
        key=call.key,
    )
