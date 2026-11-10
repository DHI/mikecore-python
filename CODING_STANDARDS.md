# Coding standards

Judgement calls for review. Formatting, lint and line endings are enforced by ruff and pre-commit; skip anything they check.

## Match the surrounding code

New code reads like the module it lands in: same decomposition, naming and idiom.

- Extend an existing class or pattern before adding a module. A new module earns its place with a responsibility no existing module holds, not as a home for a few helper lines. Example: the native wrapper classes name their library in a `libfilename` static variable (`eumDLL` in `mikecore/eum.py`); a change to how libraries load extends that pattern in each wrapper.
- Prefer the smallest diff that fits the existing structure over a cleaner structure of the agent's own.
- A type or bug fix that forces a restructure is done when its checks pass and the code names every value it introduces, down to each field, in idiomatic Python (`nodes.x` from a `NamedTuple`).

## Types state what the code really does

The type checker is part of verification, so a declared type must match every value the code handles. Fix a mismatch by changing the code or the type, not with `typing.cast` or a checker suppression; keep one only when the fix would change the public API, and give the reason on that line.

## Tests check behaviour a user sees

Tests call the public API (`mikecore.*`, `miketools.*`) against the bundled libraries and files in `testdata/`, and assert on results a user would observe.

- A test that restates the implementation (file names, loader flags, symbol tables, which code path ran) fails review.
- Mocks or stand-ins for the native libraries or MIKE engines are not accepted. When a behaviour cannot be tested with the real libraries, leave it untested and say so in the PR.

## User docs describe use, not mechanism

README text tells a user what to do, when it applies, and its limits, in a few lines. How it works belongs in code comments, commit messages or the PR.
