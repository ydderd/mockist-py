"""mockist-specific exceptions."""


class MockistError(Exception):
    """Base error for mockist harness failures."""


class SequenceExhaustedError(MockistError):
    """Raised when a sequence stub has no remaining steps."""
