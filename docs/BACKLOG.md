# Backlog

Ordered work for mockist-py. Requirements detail lives in [SPEC.md](SPEC.md); release
process in [RELEASING.md](RELEASING.md).

## Done

- [x] Repo bootstrap — spec, license, README outline
- [x] Elastic License 2.0 + `docs/LICENSING.md`
- [x] Package scaffold — `pyproject.toml`, `src/mockist`, `uv.lock`
- [x] CI — ruff, basedpyright, pytest matrix 3.10–3.13, smoke-pack
- [x] Release workflow — PyPI OIDC, changelog-driven GitHub Release
- [x] Pre-commit — ruff + format
- [x] Examples skeleton — `examples/generic/` in pytest from day one
- [x] PyPI package name decision — `mockist`

## M0 — Core harness

**Exit:** wrap a callable tool map, stub a result/error, assert the exact trajectory.

- [ ] `create_harness` + `Harness.dispatch`
- [ ] Stub matching — `args`, `match` predicate, name-only, first-match wins
- [ ] `on_unhandled` — passthrough, warn, error
- [ ] Trajectory recording
- [ ] Sequential stubs + `sequence_state()` + exhaustion modes
- [ ] `define_stubs` / layered stub registries
- [ ] Core assertion helpers (`expect_exact_trajectory`, `expect_called_with`, …)
- [ ] Generic callable adapter — `wrap_tools`
- [ ] Unit tests — harness, sequence, assertions, generic adapter
- [ ] Flesh out `examples/generic/integration.py` with runnable M0 code
- [ ] README quick start — replace placeholders with working examples

## M1 — Cassettes

**Exit:** record once, replay without calling the real tool; TS-compatible cassette v1.

- [ ] Cassette format v1 parser/writer
- [ ] Record mode — `MOCKIST_RECORD`, `harness.save()`
- [ ] Replay mode — consume-once matching, `match` / `match.ignore`, redaction sentinels
- [ ] Default redactor + custom redactor injection
- [ ] Cassette state + `expect_cassette_fully_used`, `cassette_expected_calls`
- [ ] pytest plugin — auto-save when recording
- [ ] Tests — record/replay, redaction, malformed/missing cassette
- [ ] Shared fixture cassettes copied from TypeScript mockist (compatibility CI job)
- [ ] README cassette record/replay example

## M2 — Real adapter dogfood

**Exit:** one SDK adapter + example + dogfood on a real Python agent repo.

- [ ] Pick first adapter — OpenAI Agents Python **or** MCP Python (open question)
- [ ] Implement adapter + optional extra in `pyproject.toml`
- [ ] `examples/<sdk>/` — integration.py, README, test_integration.py
- [ ] Dogfood PR/branch against a real agent codebase
- [ ] First PyPI publish — claim `mockist`, configure trusted publisher, tag `v0.1.0`

## M3 — Ecosystem adapters

Only after M2 dogfood; add frameworks when pulled by real demand.

- [ ] LangChain tool adapter
- [ ] MCP server + client polish
- [ ] LlamaIndex / PydanticAI / CrewAI / AutoGen — if needed

## Infra / docs

- [ ] `docs/LOG.md` — decisions and dogfood notes (not release notes)
- [ ] GitHub `pypi` environment for release workflow
- [ ] Claim `mockist` on PyPI + trusted publisher setup
- [ ] Optional: `mockist-spec` repo for cross-language cassette fixtures (defer until both packages ship)

## Open questions

| Question | Status | Notes |
|----------|--------|-------|
| PyPI name `mockist` vs `mockist-py` | **Resolved** — use `mockist` | Claim on PyPI before first publish |
| First real adapter target | Open | OpenAI Agents Python vs MCP Python vs LangChain |
| Cassette JSON camelCase (`recordedAt`, …) | Leaning yes | Keep TS compatibility; Python APIs stay snake_case |
| License Elastic-2.0 | **Resolved** | Matches TypeScript mockist |
| `mockist-spec` shared repo | Defer | After both packages exist |

## Non-goals (unchanged)

- Eval dashboard / hosted trace product
- HTTP/DB mocking inside tool bodies
- Declarative capability-spec DSL
- pytest as a hard dependency for core harness
- Every agent SDK as a hard dependency before one adapter dogfoods
