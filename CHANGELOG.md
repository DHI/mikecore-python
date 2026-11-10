# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `MIKECORE_PYTHON_BIN`: set it to a MIKE installation's `bin` folder to have
  mikecore use that installation's native libraries instead of its bundled
  ones, at your own risk (see README).

### Changed

- The bundled Linux libraries are renamed with a `-mikecore-python` tag, for
  example `libeum-mikecore-python.so`, so they don't collide with a MIKE
  installation's (see
  [ADR 0002](docs/adr/0002-isolate-bundled-native-libraries.md)). Code that
  loads them by name needs the new names. The Windows DLLs keep their names
  and DHI's signatures.
- **Possibly breaking:** importing mikecore no longer adds its library folder
  to `PATH` or `LD_LIBRARY_PATH`. Child processes, such as an engine started
  with `subprocess`, no longer inherit it.
- The architecture check at import requires an x86-64 CPU as well as a 64-bit
  Python.

### Fixed

- `import mikecore` works with a MIKE installation's `bin` on
  `LD_LIBRARY_PATH`, for example after sourcing `mikevars.sh`. It failed with
  `undefined symbol: _Z13fnGetLanguagev`, because the bundled libraries
  resolved their dependencies to the installation's
  ([#45](https://github.com/DHI/mikecore-python/issues/45)).
- On Linux, mikecore no longer binds to a same-named library that a MIKE
  engine in the same process loaded first (#45).
- `uv build --wheel` works with hatchling 1.31 and later, and the wheel holds
  each native library once. It held each one twice before.
- Items read from a dfs file have the reference coordinates and orientation
  stored in the file. They had the `-1e-35` defaults, whatever the file held
  ([#31](https://github.com/DHI/mikecore-python/issues/31)).
- `DfsBuilder.DeleteValueDouble` is now a property, so assigning it writes the
  file's double delete value. The property was spelled `DeleteValuedouble`, so
  `builder.DeleteValueDouble = x` set a plain attribute and was ignored. The
  misspelled name stays as an alias.
- `MapProjection.GetDefaultArea()` returns the area instead of `None`.
- `dfsSetTemporalAxis` raises for a temporal axis class it does not know,
  instead of writing no temporal axis.
- `MzCartDLL.ConvertWkt2Proj4` no longer always raises, and accepts
  `datumShiftParameters=None`.
- The `MzCartDLL` functions that return strings pass the native library a
  writable buffer and retry with the length it asks for. A projection short
  name longer than the first buffer no longer raises `ProjectionException`, and
  the `Longitude2UtmZone` and `ProjectionShortName` error messages are correct.
- `Dfs123File.ReadItemTimeStepNext` with `reshape=True` returns `None` at the
  end of the file instead of raising `AttributeError`.
- `DfsFile.Open` accepts integer modes such as `0`.
- Mesh files hold only triangles and quadrilaterals, and mikecore now enforces
  it. `MeshBuilder.Create` raises `ValueError` for a dfsu file that is not 2D,
  `MeshFile.Write` raises for an element with other than 3 or 4 nodes, and
  `MeshFile.ReadMesh` raises for such an element instead of giving it
  `ElementType` 0. A 3D dfsu was written as a mesh with a `3 21` element header
  and 6- or 8-node rows ([#68](https://github.com/DHI/mikecore-python/issues/68)).
- `DfsuBuilder.SetNodeIds` and `SetNodes` can be called in either order, and
  `SetNodes`, `SetNodeIds` or `SetElements` after `SetFromMeshFile`, without
  raising "truth value of an array is ambiguous".
- `DfsuBuilder` writes a spectral file with only directions or only
  frequencies, with a count of 0 for the missing one.
- Timestep out-of-range errors in `DfsFile.ReadItemTimeStep` and
  `WriteItemTimeStep`, and the `DfsuFile` layered-mesh error, raise their
  message instead of a `TypeError`. The `WriteItemTimeStep` message gives the
  correct range.
- `DfsFile.WriteItemTimeStep` rejects a first write to a new file other than
  item 1, timestep 0 with "No dynamic items have been written to the file yet".
- `DfsFactory.CreateCustomBlock` and `DfsDynamicItemInfo.CreateEmptyItemDataData`
  raise `ValueError` for an unsupported data type, instead of
  `UnboundLocalError`.
- `DfsFile.Open` with `DfsFileMode.Closed` raises `ValueError` instead of
  `UnboundLocalError`.
- `Dfs0ToAscii` raises an error naming the item and timestep when a read
  fails, instead of `AttributeError`.
- `DfsuBuilder.Validate` reports missing nodes and elements instead of raising
  `TypeError`, and `Setup*`/`CreateDfsu` raise a clear error instead of
  `AttributeError`.
- `DfsStaticItemBuilder.Validate` reports missing data or axis instead of
  raising `AttributeError`.
- Setting a `DfsBuilder` delete value (`DeleteValueFloat`, `DeleteValueDouble`,
  `DeleteValueByte`, `DeleteValueInt`, `DeleteValueUnsignedInt`) after
  `CreateFile` raises, as the other header setters do. It used to change the
  value after the header had been written.
- `DfsBuilder.Validate` checks every entry of a compressed file's encode key
  against the item's axis. It checked one entry per dynamic item.
- `DfsBuilder.Validate` accepts a compressed dfs1 or dfs2 file, so one can be
  created. It raised `IndexError` for any dfs1 or dfs2 encode key. A dfs1 has
  one row and one layer, so its y and z keys must be 0; a dfs2 has one layer,
  so its z key must be 0.
- `DfsBuilder.Validate` accepts an encode key on a dfs0 file without checking
  it, instead of raising `IndexError`. The native library ignores the key.
- `DfsFile.WriteItemTimeStepNext` reports data shorter than the item with its
  size, instead of raising `AttributeError`.
- `DfsuBuilder` writes the `X-coord` and `Y-coord` static items of a file with
  a geographic projection, such as `LONG/LAT`, as `eumILatLong` in degrees.
  They were `eumIGeographicalCoordinate` in metres whatever the projection.
  Files with a projected coordinate system are unchanged
  ([#47](https://github.com/DHI/mikecore-python/issues/47)).
- Reading an item's value type raises the DFS error when the native library
  reports one, instead of returning `DataValueType.Instantaneous`.

[Unreleased]: https://github.com/DHI/mikecore-python/compare/v0.3.a1...HEAD
