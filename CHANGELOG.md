# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

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
- `eumWrapper.eumGetNextEqvUnit` returns the units equivalent to the base unit.
  It read the native return code the wrong way round, so it reported no unit
  where there was one, and raised `ValueError` after the last one, where the
  native description is null.
- `DfsuBuilder.SetElementIds` stores the ids, so the file has them instead of
  the default 1, 2, .... `SetElementIds` and `SetNodeIds` accept int64 arrays
  and lists and store int32 ids. Int64 node ids raised "Data type not
  supported: int64" in `CreateFile`.
- `MeshBuilder.SetNodes` keeps z as doubles, as mesh files store it, instead of
  rounding it to float32. Float32 z passed to `SetNodes`, such as
  `DfsuFile.Z`, is now written with the double text of those float32 values
  (`-1.7859922647476196` rather than `-1.7859923`). `MeshBuilder.Create(dfsuFile)`
  is unchanged.
- `miketools.Dfs0ToAscii` converts item times from the time axis unit to
  seconds, so a file with a time unit other than seconds gets the right
  timestamps. A 10 minute step was written as 10 seconds.
- `DfsFile.ReadStaticItem` raises `ValueError` for an item number below 1. It
  returned the first static item, numbered 0 or below. A number past the last
  item still returns `None`.
- `DfsFile.ReadItemTimeStepNext` and `ReadItemTimeStep` with `reshape=True`
  reshape an item with a 2-D or 3-D spatial axis to the axis shape, as
  `Dfs2File` and `Dfs3File` do. A file opened with
  `DfsFileFactory.DfsGenericOpen` ignored `reshape`. 0-D and 1-D items stay
  flat.
- A `DfsDynamicItemBuilder` can be reused after `GetDynamicItemInfo`. It
  replaced its item with a blank one but kept its "is set" flags, so the next
  item passed validation with no name, quantity or value type. The builder now
  keeps its settings for the next item, and changing it no longer changes the
  item it returned. Associated static items carry over and add up: after an
  item with static item 1, `SetAssociatedStaticItem(2)` gives the next item
  `[1, 2]`.
- Changing a `DfsStaticItemBuilder` after `GetStaticItem`, or the data array it
  holds, no longer changes the static item it returned.
- `DfsuBuilder` creates `DfsuSpectral0D` files. It raised an `Exception` with
  no message. The caller supplies the frequency-direction mesh, one element per
  frequency and direction, and `Validate` reports a Spectral0D builder with no
  frequencies or directions, or an element count that does not match them, so
  the file reads back as `DfsuSpectral0D`.

[Unreleased]: https://github.com/DHI/mikecore-python/compare/v0.3.a1...HEAD
