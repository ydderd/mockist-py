"""Package smoke tests."""

from __future__ import annotations

import mockist


def test_version_is_string() -> None:
    assert isinstance(mockist.__version__, str)
    assert mockist.__version__
