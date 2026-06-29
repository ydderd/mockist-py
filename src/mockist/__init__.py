"""mockist — local test harness for agent tool/skill boundaries."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("mockist")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = ["__version__"]
