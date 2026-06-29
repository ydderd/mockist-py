"""Dotted path utilities for cassette matching."""

from __future__ import annotations

import copy
import json
import re
from typing import Any

from mockist.cassette.redact import is_redacted

PathToken = str | int


def parse_path(path: str) -> list[PathToken]:
    tokens: list[PathToken] = []
    for segment in path.split("."):
        name_match = re.match(r"^[^[]+", segment)
        if name_match:
            tokens.append(name_match.group(0))
        for index_match in re.finditer(r"\[(\d+)\]", segment):
            tokens.append(int(index_match.group(1)))
    return tokens


def _delete_at_path(root: Any, path: str) -> None:
    tokens = parse_path(path)
    cur: Any = root
    for token in tokens[:-1]:
        if not isinstance(cur, (dict, list)):
            return
        if isinstance(cur, list) and isinstance(token, int):
            cur = cur[token]
        elif isinstance(cur, dict) and isinstance(token, str):
            cur = cur.get(token)
        else:
            return
    last = tokens[-1]
    if isinstance(cur, dict) and last in cur:
        del cur[last]
    elif isinstance(cur, list) and isinstance(last, int) and 0 <= last < len(cur):
        del cur[last]


def _clone_for_blanking(root: Any, seen: dict[int, Any] | None = None) -> Any:
    if seen is None:
        seen = {}
    obj_id = id(root)
    if obj_id in seen:
        return seen[obj_id]
    if isinstance(root, list):
        copy_list = [_clone_for_blanking(item, seen) for item in root]
        seen[obj_id] = copy_list
        return copy_list
    if isinstance(root, dict):
        copy_dict = {k: _clone_for_blanking(v, seen) for k, v in root.items()}
        seen[obj_id] = copy_dict
        return copy_dict
    return root


def blank_paths(root: Any, paths: list[str]) -> Any:
    if not paths:
        return root
    try:
        clone = copy.deepcopy(root)
    except Exception:
        try:
            clone = json.loads(json.dumps(root))
        except Exception:
            clone = _clone_for_blanking(root)
    for path in paths:
        _delete_at_path(clone, path)
    return clone


def find_redacted_paths(value: Any, base: str) -> list[str]:
    out: list[str] = []

    def walk(current: Any, path: str) -> None:
        if isinstance(current, str):
            if is_redacted(current):
                out.append(path)
            return
        if isinstance(current, list):
            for i, item in enumerate(current):
                walk(item, f"{path}[{i}]")
            return
        if isinstance(current, dict):
            for key, item in current.items():
                walk(item, f"{path}.{key}")

    walk(value, base)
    return out
