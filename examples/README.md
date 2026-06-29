# mockist-py examples

**Start here:** each adapter has an `integration.py` with commented, copy-pasteable wiring
code. Tests verify that file loads and references the intended API — read `integration.py`
first.

Not sure your stack is supported? See the [compatibility table](../README.md#compatibility)
in the README. Full requirements: [docs/SPEC.md](../docs/SPEC.md).

| Adapter | Integration code | Walkthrough |
|---------|------------------|-------------|
| Generic callables | [`generic/integration.py`](./generic/integration.py) | [`generic/README.md`](./generic/README.md) |

## Layout

```
examples/
  <adapter>/
    README.md           ← call flow, hook shapes, minimal snippet
    integration.py      ← **the code to copy** (heavily commented)
    test_integration.py ← CI checks integration.py (thin)
```

## Import path

`integration.py` files import `mockist` from the editable package while developing in this
repo. In your app:

```py
from mockist import create_harness, wrap_tools  # M0 — not implemented yet
```

## Universal pattern (M0 target)

```py
# 1. Declare boundary stubs
harness = create_harness(stubs=[...], on_unhandled="error")

# 2. Wrap at your tool boundary
tools = wrap_tools({"get_weather": get_weather}, harness)

# 3. Run agent
result = await run_agent(prompt="...", tools=tools)

# 4. Assert trajectory
assert expect_called_with(harness.trajectory, "get_weather", {"city": "Paris"}).pass_
```

## Run

```bash
uv run pytest                    # unit tests + all examples
uv run pytest examples/generic   # one adapter
```
