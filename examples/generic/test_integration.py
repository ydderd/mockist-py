"""CI guard for examples/generic/integration.py."""

from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_integration_module():
    path = Path(__file__).with_name("integration.py")
    spec = importlib.util.spec_from_file_location("generic_integration", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_integration_module_loads() -> None:
    module = _load_integration_module()
    assert module.GUIDE_VERSION
    assert module.TARGET_APIS == (
        "create_harness",
        "wrap_tools",
        "expect_called_with",
    )


def test_integration_documents_target_apis() -> None:
    source = Path(__file__).with_name("integration.py").read_text(encoding="utf-8")
    for name in ("create_harness", "wrap_tools", "expect_called_with"):
        assert name in source
