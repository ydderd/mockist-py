# Implementation checklist

Status: `done`
Plan: `.cursor/plans/implement_mockist-py_be510296.plan.md`
Last updated: 2026-06-29 by agent

## M0 — Core harness
- [x] types, identity, deep_equal, recorder, errors
- [x] registry + harness (dispatch, sequences, resolve/record/capture)
- [x] assertions + composition
- [x] wrap_tools + M0 tests
- [x] examples/generic runnable + README quick start

## M1 — Cassettes
- [x] cassette/ modules (format, io, paths, match, redact, replay, record, registry)
- [x] harness record/replay integration + save buffer
- [x] cassette assertions + pytest flush plugin
- [x] cassette tests + fixtures/cassettes compat suite

## M2 — Adapters
- [x] openai adapter + tests
- [x] mcp adapter + tests
- [x] langchain adapter + tests
- [x] cross-adapter parity test

## M2 — Examples
- [x] examples/openai, examples/mcp, examples/langchain

## Ship
- [x] public API exports in __init__.py
- [x] BACKLOG + CHANGELOG updated
- [x] full CI green (ruff, basedpyright, pytest, smoke_pack)
