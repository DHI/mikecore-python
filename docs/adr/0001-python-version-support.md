# 1. Support only Python versions that have not reached end of life

Date: 2026-10-07

## Status

Accepted

## Context

mikecore declared `requires-python = ">=3.5"`, but CI only tested 3.8 and 3.14,
and ruff targeted 3.8. Nothing checked that the code still ran on 3.5–3.7. The
declared floor was a promise we did not test.

CPython releases a new minor version each October. Each release gets about
five years of support: bug-fix releases first, then security fixes only. After
that it reaches end of life and gets no more fixes, not even for security. The
schedule is published at <https://devguide.python.org/versions/>.

As of this decision:

| Version | End of life |
| ------- | ----------- |
| 3.10    | 2026-10 (reached) |
| 3.11    | 2027-10     |
| 3.12    | 2028-10     |
| 3.13    | 2029-10     |
| 3.14    | 2030-10     |

numpy, our only runtime dependency, already supports only recent Python
versions (see [SPEC 0](https://scientific-python.org/specs/spec-0000/)). So users
on an end-of-life interpreter are already stuck on old numpy releases.

## Decision

mikecore supports only CPython versions that are listed as supported on the
Python devguide, i.e. not end of life. Today that means **Python 3.11 and newer**.

- `requires-python` in `pyproject.toml` is set to the oldest supported version.
  Ruff takes its target version from it, so lint does not flag syntax that the
  oldest supported version understands.
- CI tests the oldest and the newest supported versions on Windows and Linux.
- When a version reaches end of life, the next release of mikecore may raise
  `requires-python` and update CI to match. It is not a breaking change in the
  semantic-versioning sense. pip and uv will keep installing the last
  compatible mikecore on the old interpreter.
- Code may use any language or standard-library feature available in the
  oldest supported version.

## Consequences

- Users on Python 3.10 or older stay on the last mikecore release that
  supported their interpreter and get no new releases.
- The codebase can use modern syntax: `X | Y` unions, built-in generics
  (`list[int]`), f-strings, `match`, exception groups and `tomllib`. Ruff's
  pyupgrade (`UP`) rules are enabled and enforce this.
- CI covers every version we claim to support at both ends of the range, so the
  declared floor is tested.
- Each October someone needs to bump the floor. The table above and the CI
  matrix should be updated at the same time.
