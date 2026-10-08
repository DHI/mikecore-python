# AGENTS.md

- Review changes against `CODING_STANDARDS.md`.
- Check with `uvx pre-commit run --all-files` (ruff and line endings, as CI's `lint.yml` does) and `uv run pytest`.
- Native libraries: the hatch build hook `buildUtil/build.py` downloads the NuGet packages in `buildUtil/packages.config` into `packages/` and copies them to `mikecore/bin/{windows,linux}`; on Linux it sets RPATH `$ORIGIN`. Inspect `mikecore/bin/` after `uv sync`, not the NuGet sources.
- Test data lives in the root `testdata/`, not `tests/testdata/`.
- `uv.lock` is gitignored. Push branches to `origin` (DHI/mikecore-python); PRs target `master`.
