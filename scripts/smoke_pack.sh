#!/usr/bin/env bash
# Smoke-test the wheel the way consumers install it.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "smoke-pack: sync dev environment"
uv sync --frozen

echo "smoke-pack: build sdist and wheel"
uv build --out-dir "$TMP/dist"

WHEEL="$(find "$TMP/dist" -name '*.whl' | head -n 1)"
if [[ -z "$WHEEL" ]]; then
  echo "smoke-pack: no wheel found in $TMP/dist" >&2
  exit 1
fi

echo "smoke-pack: install wheel in isolated venv ($WHEEL)"
uv venv "$TMP/venv"
# shellcheck disable=SC1091
source "$TMP/venv/bin/activate"
uv pip install "$WHEEL"

echo "smoke-pack: import mockist and read version"
python -c "import mockist; print('mockist', mockist.__version__)"

echo "smoke-pack: ok"
