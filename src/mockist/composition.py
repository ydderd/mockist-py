"""Multi-harness trajectory composition."""

from __future__ import annotations

from mockist.types import Call


def concat_trajectories(*segments: list[Call]) -> list[Call]:
    out: list[Call] = []
    for segment in segments:
        out.extend(segment)
    return out


def merge_harness_trajectories(*harnesses: object) -> list[Call]:
    from mockist.harness import Harness

    return concat_trajectories(*[h.trajectory for h in harnesses if isinstance(h, Harness)])
