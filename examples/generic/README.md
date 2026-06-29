# Generic callable adapter

Wrap a `dict[str, Callable]` (sync or async) at the tool boundary.

## Call flow

```
agent → wrapped_tools[name](input) → harness.dispatch → stub | passthrough → trajectory
```

## Status

M0 — `create_harness` and `wrap_tools` are specified in [docs/SPEC.md](../docs/SPEC.md) but
not implemented yet. `integration.py` documents the target wiring.

## Minimal snippet (target API)

```py
from mockist import create_harness, expect_called_with, wrap_tools

harness = create_harness(
    on_unhandled="error",
    stubs=[{"name": "get_weather", "args": {"city": "Paris"}, "result": {"temp_c": 21}}],
)
tools = wrap_tools({"get_weather": get_weather}, harness)
```

See [`integration.py`](./integration.py) for the full commented guide.
