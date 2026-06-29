"""Pending cassette save registry."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

SaveThunk = Callable[[], None | Awaitable[None]]

_pending: list[SaveThunk] = []


def register_pending_save(save: SaveThunk) -> None:
    _pending.append(save)


async def flush_pending_saves() -> None:
    todo = _pending[:]
    _pending.clear()
    for save in todo:
        result = save()
        if hasattr(result, "__await__"):
            await result  # type: ignore[misc]
