# 2. Isolate the bundled native libraries from a MIKE installation's

Date: 2026-11-10

## Status

Accepted

## Context

mikecore bundles its own build of the MIKE Core native libraries (`ufs`, `eum`,
`pfs2004`, `MzCart` and others, plus Intel runtime libraries on Linux). A MIKE
installation ships its own, usually newer, builds under the same names.
Libraries with the same name get mixed up
([#45](https://github.com/DHI/mikecore-python/issues/45)):

- On Linux, with an installation's `bin` on `LD_LIBRARY_PATH` (for example
  after sourcing `mikevars.sh`), mikecore's libraries resolved their
  dependencies to the installation's copies, and `import mikeio` failed with
  `undefined symbol: _Z13fnGetLanguagev`. The libraries had DT_RUNPATH, which
  the loader searches after `LD_LIBRARY_PATH`.
- On Linux and Windows, the loader keeps one library per name. If a MIKE engine
  in the same process loaded its copy first, mikecore's libraries would bind
  to it.

Two goals pull against each other. Isolation keeps mikecore working whatever
MIKE version is installed. Sharing one set of libraries with an engine lets the
two exchange handles in one process, and makes version drift visible instead
of hiding it. A build system that compiled mikecore against the installed MIKE
Core would serve both; until then, this is an interim decision.

## Decision

mikecore uses its bundled libraries, isolated, by default. A user can opt in to
an installation's libraries instead.

- **Unique names.** The build adds `-mikecore-python` to every bundled
  library's name (`ufs.dll` -> `ufs-mikecore-python.dll`, `libeum.so` ->
  `libeum-mikecore-python.so`), and rewrites the libraries' references to each
  other to match: SONAMEs and NEEDED entries with patchelf on Linux, import
  tables with pefile on Windows.
- **DT_RPATH `$ORIGIN` on Linux**, which the loader searches before
  `LD_LIBRARY_PATH`, so dependencies always resolve to the bundled folder.
- **No environment edits at import.** mikecore no longer changes `PATH` or
  `LD_LIBRARY_PATH`. On Windows it adds its folder with `os.add_dll_directory`
  only while it loads its DLLs.
- **Opt-in `MIKECORE_PYTHON_BIN`.** Set to an installation's `bin` folder,
  mikecore loads that folder's libraries under their own names, so an engine
  in the same process shares them. This is at the user's own risk: mikecore is
  tested only with its bundled libraries.
- **No `RTLD_DEEPBIND`.** It would also isolate mikecore from libraries loaded
  with `RTLD_GLOBAL`, but it bypasses an `LD_PRELOAD` allocator (tcmalloc or
  jemalloc, common with Colab, PyTorch and Dask), which corrupts the heap, and
  it made the Intel OpenMP runtime crash on startup.
- **No auditwheel.** It would do the Linux renaming too, but it bundles the
  system libraries the wheel needs, including LGPL ones, which needs a
  licensing review.

## Consequences

- mikecore imports and works next to any MIKE installation, on either
  platform, in either import order, as long as the engine doesn't load its
  libraries with `RTLD_GLOBAL`.
- An engine whose library is loaded with `RTLD_GLOBAL` before `import
  mikecore` can still take over mikecore's symbols, because
  `libFemInterface.so` contains its own copy of MIKE Core. Callers load such
  libraries with `RTLD_LOCAL`, or import mikecore first. This is documented in
  #45, not worked around.
- Patching invalidates DHI's Authenticode signature on the Windows DLLs that
  import other bundled DLLs, so the build removes it. Those DLLs are unsigned
  in the wheel; this matters only where a policy (WDAC, AppLocker, antivirus)
  requires DHI's signature.
- The bundled libraries' version can drift from the installation's without
  anyone noticing. `MIKECORE_PYTHON_BIN` is the way to check mikecore against
  an installation's libraries.
- Code that names a bundled library must use the tagged name, which each
  wrapper's `libfilename` holds. If it doesn't match the built files, `import
  mikecore` fails, so the whole test suite does. The build checks its own
  output: it fails if a bundled library still refers to another by its
  untagged name.
