# Releasing mockist (Python)

## CI (every PR and push to `main`)

Workflow: [`.github/workflows/ci.yml`](../.github/workflows/ci.yml)

1. `uv sync --frozen`
2. `uv run ruff check` and `uv run ruff format --check`
3. `uv run basedpyright`
4. `uv run pytest` on Python **3.10, 3.11, 3.12, 3.13**
5. `./scripts/smoke_pack.sh` — builds sdist/wheel, installs in a temp venv, imports `mockist`

Examples under `examples/` are included in pytest from day one (`testpaths` in `pyproject.toml`).

## CD (PyPI + GitHub Release)

Workflow: [`.github/workflows/release.yml`](../.github/workflows/release.yml)

Publishing uses **[PyPI trusted publishing](https://docs.pypi.org/trusted-publishers/)**
(OIDC from GitHub Actions). No long-lived `PYPI_API_TOKEN` secret is required once configured.

### One-time setup: PyPI trusted publisher

Requirements:

- Public GitHub repo: `ydderd/mockist-py`
- Package name on PyPI: `mockist` (claim manually if unavailable)
- Trusted publisher on [pypi.org](https://pypi.org) → package settings → **Publishing** → **Add a new pending publisher** or configure on existing package

| Field | Value |
|-------|-------|
| **PyPI Project Name** | `mockist` |
| **Owner** | `ydderd` |
| **Repository name** | `mockist-py` |
| **Workflow name** | `release.yml` |
| **Environment name** | `pypi` (optional; must match workflow if set) |

#### Step 1 — First publish (one time only)

If `mockist` is not on PyPI yet, publish once manually or claim the name:

```bash
uv sync
uv build
uv publish   # maintainer account with 2FA; or twine upload dist/*
```

Install:

```bash
pip install mockist
# optional extras: pip install "mockist[pytest]"
```

#### Step 2 — Harden publishing access (recommended after OIDC works)

On PyPI package **Settings → Publishing**:

- Prefer trusted publishing over API tokens
- Revoke legacy tokens you no longer need

### Publish a version

1. Move **[Unreleased]** entries in `CHANGELOG.md` into a new `## [x.y.z] - YYYY-MM-DD`
   section (keep compare links at the bottom up to date).
2. Bump version with **uv** (updates `pyproject.toml` only):

   ```bash
   uv version 0.1.0        # set exact version
   # or: uv version patch | minor | major
   ```

3. Commit, push to `main`, and tag:

   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "chore: release v0.1.0"
   git tag v0.1.0
   git push origin main --tags
   ```

4. The release workflow runs on tag push `v*.*.*`:
   - Full test matrix + smoke pack
   - `uv build` → publish to PyPI via OIDC
   - GitHub Release with the matching `CHANGELOG.md` section as the release body
     (`CHANGELOG.md` attached as a release asset)

### Manual release (re-run an existing tag)

Use **Actions → Release → Run workflow** and pass the tag (e.g. `v0.1.0`).

### Local preflight

```bash
uv sync
uv run ruff check && uv run ruff format --check
uv run basedpyright
uv run pytest
./scripts/smoke_pack.sh
uv build
```

Prefer the release workflow for publishes so provenance and GitHub Release stay in sync.

## Versioning with uv

`uv version` is the single source of truth — it edits `[project].version` in `pyproject.toml`.
Do not hand-edit version in multiple places.

```bash
uv version              # print current
uv version patch        # 0.1.0 -> 0.1.1
uv version minor        # 0.1.1 -> 0.2.0
uv version major        # 0.2.0 -> 1.0.0
uv version 1.2.3        # set explicitly
```

Tag must match: `v` + `pyproject.toml` version (e.g. `v0.1.0`).
