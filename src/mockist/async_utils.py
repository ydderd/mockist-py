"""Async helpers for sync/async callables."""

from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

T = TypeVar("T")


async def await_maybe(value: T | Awaitable[T]) -> T:
    if inspect.isawaitable(value):
        return await value  # type: ignore[misc]
    return value


async def invoke_callable(fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    result = fn(*args, **kwargs)
    return await await_maybe(result)
