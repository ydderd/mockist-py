# Changelog

All notable changes to **mockist** (Python) are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Release process: bump version with `uv version`, move items from **[Unreleased]** into a
dated version section, tag `v*.*.*`, push — see [docs/RELEASING.md](docs/RELEASING.md).

Development decisions and dogfood notes (not release notes) live in
[docs/LOG.md](docs/LOG.md) when that file exists. Ordered work: [docs/IMPLEMENTATION.md](docs/IMPLEMENTATION.md).

## [Unreleased]

### Added

- Core harness — `create_harness`, stubs, sequential stubs, trajectory recording, `on_unhandled` policies
- Trajectory assertions — `expect_exact_trajectory`, `expect_called_with`, `expect_cassette_fully_used`, and related helpers
- Cassette format v1 — record/replay via `MOCKIST_RECORD`, redaction, consume-once matching (TS-compatible JSON)
- Adapters — `wrap_tools`, `wrap_openai_tools`, `wrap_mcp_handlers`, `create_mcp_client_interceptor`, `wrap_langchain_tools`
- pytest plugin — `mockist_assert` fixture and auto-flush on record
- Examples and tests for generic, OpenAI, MCP, and LangChain wiring
- Cross-language cassette fixtures under `tests/fixtures/cassettes/`

## [0.0.0] - 2026-06-29

Repository bootstrap (spec, license, README outline, CI scaffold).

[Unreleased]: https://github.com/ydderd/mockist-py/compare/v0.0.0...HEAD
[0.0.0]: https://github.com/ydderd/mockist-py/releases/tag/v0.0.0
