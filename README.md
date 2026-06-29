# mockist-py

Unit test the tool calls your agent makes: which tool, what args, what order,
what result or error, and whether real code ran.

mockist-py wraps the **agentic tool/skill boundary**. It does not mock the LLM,
provider SDK, database, HTTP client, queue, or the internals of a tool's `execute`.
It only controls and records the boundary where the agent calls your tools.

**Status:** early — implementation spec only. See [docs/SPEC.md](docs/SPEC.md).

The TypeScript package ([@ydderd/mockist](https://github.com/ydderd/mockist)) is the
shipping reference implementation and cassette format v1 authority.

## At a glance

| | |
|---|---|
| **What it is** | A local test harness for agent **tool-call trajectories** — stubs, cassettes, assertions |
| **What it tests** | Did the agent call the right tool/skill, with the right args, in the right order? |
| **What it does not test** | Code *inside* a tool's body (DB, HTTP, queues) — use `unittest.mock`, `responses`, `respx`, testcontainers |
| **Language** | Python **3.10+** ([mockist](https://github.com/ydderd/mockist) for TypeScript) |
| **Model** | Bring your own scripted/mock model — mockist-py does not stub the LLM |

**Good fit:** you pass a tools dict (or MCP handlers / SDK tool callbacks) to an agent and want fast, deterministic CI tests for tool-use behavior.

**Poor fit:** you need to prove `execute` talks to Postgres correctly, or you use a framework with no hook/wrap point at the tool boundary (see [compatibility](#compatibility) below).

```bash
# Not published yet — install from source once pyproject.toml lands
pip install mockist
# or: pip install mockist-py
```

## Compatibility

### Planned (MVP)

| Library / surface | Adapter | Status |
|-------------------|---------|--------|
| Generic callables | `wrap_tools(tools, harness)` | M0 |
| [OpenAI Agents Python](https://github.com/openai/openai-agents-python) | `wrap_openai_tools(tools, harness)` | M2 |
| MCP **server** handlers | `wrap_mcp_handlers(handlers, harness)` | M2 |
| MCP **client** calls | `create_mcp_client_interceptor(harness)` | M2 |
| [LangChain](https://python.langchain.com/) tools | `wrap_langchain_tools(tools, harness)` | M3 (optional extra) |
| pytest | `mockist_assert` fixture / plugin | M1 (optional extra) |

Runnable wiring for each row: [`examples/`](examples/) (coming soon).

### Not supported (use something else)

| You need | Why mockist-py is not the tool | Use instead |
|----------|-------------------------------|-------------|
| Stub HTTP/DB/queue **inside** `execute` | That is implementation unit testing, not the agent boundary | `unittest.mock`, `responses`, `respx`, `pytest-httpx`, `vcrpy`, testcontainers |
| Mock the LLM / model routing | Out of scope — mockist-py sits below the model, at tool dispatch | SDK mock models, fixture responses |
| **Vercel AI SDK**, **Claude Agent SDK** | TypeScript-only surfaces today | [@ydderd/mockist](https://github.com/ydderd/mockist) |
| **LlamaIndex**, **CrewAI**, **AutoGen**, **PydanticAI** | No first-party adapter yet | Wrap at your framework's tool boundary yourself, or open an issue |
| TypeScript / Node | Separate package | [@ydderd/mockist](https://github.com/ydderd/mockist) |

If your stack is "tools with a local callback passed to an agent loop," mockist-py likely fits. If tool calls never converge on a single dispatch point you can wrap, fix that first or pick a narrower test layer.

## Why

Agent tests often fail in one of two ways:

- They mock too low, so the test proves your DB/HTTP mocks work but not that the
  agent called the right tool.
- They run live, so failures are slow, expensive, and hard to reproduce.

mockist-py gives you a middle layer: deterministic tests for the agent's tool-use
behavior.

## Quick start

<!-- Filled in when M0 lands -->

In your existing test, wrap the tools before passing them to the agent:

```py
from mockist import create_harness, expect_called_with, wrap_tools

harness = create_harness(
    on_unhandled="error",
    stubs=[
        {
            "name": "get_weather",
            "args": {"city": "Paris"},
            "result": {"city": "Paris", "temp_c": 21},
        },
    ],
)

tools = wrap_tools({"get_weather": get_weather}, harness)
result = await run_agent(prompt="What's the weather in Paris?", tools=tools)

assert "21" in result.text
assert expect_called_with(harness.trajectory, "get_weather", {"city": "Paris"}).pass_
```

`run_agent` is your app's agent entry point. `get_weather` is your real tool callable.
mockist-py sits between them.

## Stubbed error example

<!-- Filled in when M0 lands -->

```py
harness = create_harness(
    on_unhandled="error",
    stubs=[
        {
            "name": "search",
            "args": {"q": "billing"},
            "result": lambda _input: (_ for _ in ()).throw(RuntimeError("upstream 503")),
        },
    ],
)
```

## Record and replay

Cassettes are a feature, not the whole product: record a real tool-boundary run
once, then replay the tool results in local/CI tests. Format is compatible with
[@ydderd/mockist](https://github.com/ydderd/mockist) cassette v1.

<!-- Filled in when M1 lands -->

```py
harness = create_harness(
    cassette="fixtures/weather_flow.json",
    on_unhandled="error",
)
```

```bash
MOCKIST_RECORD=1 pytest tests/test_weather_flow.py  # records real tool outputs
pytest tests/test_weather_flow.py                   # replays from the cassette
```

The cassette stores tool name, input, output or error, and match rules. It does
not record HTTP/DB calls inside your tool.

## What you can test

| Need | Use |
|------|-----|
| Return canned tool output | `stubs=[{"name", "args", "result"}]` |
| Inject a tool failure | `"error": TimeoutError("upstream timeout")` or callable |
| Test retries or polling | `"sequence": [{"error": ...}, {"result": ...}]` |
| Fail on unexpected tool calls | `on_unhandled="error"` |
| Assert call order and args | `harness.trajectory` + assertion helpers |
| Freeze one live run | `cassette="fixtures/flow.json"` + `MOCKIST_RECORD=1` |

## Docs map

- [Spec](docs/SPEC.md): full implementation requirements and milestones
- [Licensing](docs/LICENSING.md): Elastic License 2.0 summary for adopters
- [mockist (TypeScript)](https://github.com/ydderd/mockist): shipping reference, cassette format, examples

## What not to use this for

mockist-py is not a replacement for unit tests of tool internals. If you own the
tool body, test its DB/HTTP/queue behavior with normal tools such as `unittest.mock`,
`responses`, `respx`, or testcontainers.

mockist-py is also not an eval dashboard. It is a local, in-repo test harness for
tool-call behavior.

## License

[Elastic License 2.0](LICENSE) — source-available, including commercial use, with
the limits described in the license. See [docs/LICENSING.md](docs/LICENSING.md)
for the practical summary.
