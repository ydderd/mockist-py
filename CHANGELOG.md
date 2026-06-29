# Changelog

All notable changes to **mockist** (Python) are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Release process: bump version with `uv version`, move items from **[Unreleased]** into a
dated version section, tag `v*.*.*`, push — see [docs/RELEASING.md](docs/RELEASING.md).

Development decisions and dogfood notes (not release notes) live in
[docs/LOG.md](docs/LOG.md) when that file exists. Ordered work: [docs/BACKLOG.md](docs/BACKLOG.md).

## [Unreleased]

### Added

- Project scaffold: `pyproject.toml`, CI/release workflows, pre-commit, smoke-pack script
- Minimal `mockist` package skeleton and pytest plugin stub
- `examples/generic/` integration guide with day-one CI coverage

## [0.0.0] - 2026-06-29

Repository bootstrap (spec, license, README outline).

[Unreleased]: https://github.com/ydderd/mockist-py/compare/v0.0.0...HEAD
[0.0.0]: https://github.com/ydderd/mockist-py/releases/tag/v0.0.0
