# AGENTS.md

- Review changes against `CODING_STANDARDS.md`.
- Check with `uvx pre-commit run --all-files` (ruff and line endings, as CI's `lint.yml` does) and `uv run pytest`.
- Native libraries: the hatch build hook `buildUtil/build.py` downloads the NuGet packages in `buildUtil/packages.config` into `packages/` and copies them to `mikecore/bin/{windows,linux}`; on Linux it sets RPATH `$ORIGIN`. Inspect `mikecore/bin/` after `uv sync`, not the NuGet sources.
- Test data lives in the root `testdata/`, not `tests/testdata/`.
- `uv.lock` is gitignored. Push branches to `origin` (DHI/mikecore-python); PRs target `master`.

## Tests

- Tests live in `tests/` and use only the public `mikecore` API. Ask before editing `mikecore/` to make something testable.
- Expected values come from outside production code: the DFS/MIKE Core spec, a hand calculation, or a reference tool (MIKE Zero, the .NET MIKE Core SDK, a file in `testdata/` written by MIKE).
- Fixtures use a distinct value per element, so a swapped axis, reversed order, or wrong offset shows up. Grids are non-square (e.g. dfs2 with `nx != ny`); sequences are non-palindromic and non-constant.
- A test is done once you have seen it fail.
