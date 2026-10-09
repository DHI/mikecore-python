# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

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
- A null string from the native library raises `ValueError` instead of
  `AttributeError` in `eum` and `DfsFile`.
- `DfsDLL.Init` and `MzCartDLL.Init` without a library path raise `ValueError`
  instead of `TypeError`.
- `DfsuBuilder` no longer raises `UnboundLocalError` on unexpected input.

[Unreleased]: https://github.com/DHI/mikecore-python/compare/v0.3.a1...HEAD
