# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `DfsuFile.SubMeshType` tells whether a dfsu file from MIKE 2027 has a
  local refinement submesh: 1 if it has, 0 if not, and `None` for a file
  without a submesh type. Compare it with `None`, as a plain truth test is
  false for submesh type 0
  ([#54](https://github.com/DHI/mikecore-python/issues/54)).
- `DfsuBuilder.SetSubMeshType(None | 0 | 1)` writes a dfsu file with a
  submesh type, as MIKE 2027 does. Without it, older mikecore releases can
  still open the file. With it, they can only open a 2D file with submesh
  type 0.
- `MIKECORE_PYTHON_BIN`: set it to a MIKE installation's `bin` folder to have
  mikecore use that installation's native libraries instead of its bundled
  ones, at your own risk (see README).
- A required `source` attribute in `buildUtil/packages.config` picks where the
  build downloads the native NuGet packages from: `nuget.org`, or
  `github-mirror` for a mirror on this repository's releases.
- `eumItem` and `eumUnit` entries for the 2026 EUM table: the items
  `eumIFreqIntegWaveActionDensity`, `eumIDirecIntegWaveActionDensity` and
  `eumIFreqIntegWaveEnergyDensityRate`, and the units `eumUm2Sec2`,
  `eumUft2Sec2`, `eumUm2SecRad` and `eumUft2SecRad`.

### Changed

- The bundled Linux libraries are renamed with a `-mikecore-python` tag, for
  example `libeum-mikecore-python.so`, so they don't collide with a MIKE
  installation's (see
  [ADR 0002](docs/adr/0002-isolate-bundled-native-libraries.md)). Code that
  loads them by name needs the new names. The Windows DLLs keep their names.
- **Possibly breaking:** the bundled native libraries are the 2026 GOLD
  versions: DHI.DFS, DHI.PFS, DHI.EUM, DHI.DHIfl and DHI.Projections 24.1.2,
  and DHI.MikeCore.Linux.ubuntu22 24.0.2 (previously all 23.0.3). They're
  downloaded from the GitHub mirror on this repository's releases until
  nuget.org publishes them. The bundled Windows DLLs are unsigned for now,
  which policies such as WDAC or AppLocker may block.
- **Possibly breaking:** importing mikecore no longer adds its library folder
  to `PATH` or `LD_LIBRARY_PATH`. Child processes, such as an engine started
  with `subprocess`, no longer inherit it.
- The architecture check at import requires an x86-64 CPU as well as a 64-bit
  Python.

### Fixed

- On Linux, mikecore no longer needs `libnsl2` installed, which Ubuntu 24.04
  doesn't install by default. The bundled Xerces library was linked against it
  without using it
  ([#59](https://github.com/DHI/mikecore-python/issues/59)).
- `DfsuFile` opens dfsu files from MIKE 2027 with a submesh type, such as 3D
  files and locally refined meshes, which raised "not a valid dfsu file".
  Files from later MIKE versions with more custom block values also open.
  Legacy Spectral0D (rose-plot) files still open as `DfsuSpectral0D`,
  including files with frequencies only or directions only
  ([#54](https://github.com/DHI/mikecore-python/issues/54)).
- A failed open of a dfs file shorter than 4 bytes, such as an empty file, no
  longer leaves the file open. Each such open used up a file handle, so after
  about 500 of them no file could be opened (Error code 2003)
  ([#85](https://github.com/DHI/mikecore-python/issues/85)).
- `import mikecore` works with a MIKE installation's `bin` on
  `LD_LIBRARY_PATH`, for example after sourcing `mikevars.sh`. It failed with
  `undefined symbol: _Z13fnGetLanguagev`, because the bundled libraries
  resolved their dependencies to the installation's
  ([#45](https://github.com/DHI/mikecore-python/issues/45)).
- On Linux, mikecore no longer binds to a same-named library that a MIKE
  engine in the same process loaded first (#45).
- `uv build --wheel` works with hatchling 1.31 and later, and the wheel holds
  each native library once. It held each one twice before.
- In a dfs file opened for editing, a dynamic item's changed `Name` or newly
  assigned `Quantity` is written to the file on `Close`, and in Edit mode
  also on `Flush`. As in the
  C# library, a new name is truncated or padded with spaces to the length of
  the old one, and changing `Quantity.Item` or `Quantity.Unit` in place is not
  written. A name that cp1252 cannot encode raises `UnicodeEncodeError`, and
  a name containing a NUL character or a unit that is not a unit of the item
  raises `ValueError`, before any item is written
  ([#38](https://github.com/DHI/mikecore-python/issues/38)).
- `DfsuFile.Flush()` flushes the file instead of raising `TypeError`, and
  `DfsFileFactory.DfsuFileOpenAppend` no longer requires `parameters`, like the
  other `Open` methods.
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

## [0.2.2] - 2024-08-21

### Fixed

- The package declares a valid required Python version, `>=3.5`. Earlier
  releases declared `>=3.5<`, which is not a valid version specifier
  ([#29](https://github.com/DHI/mikecore-python/issues/29)).

## [0.2.1] - 2022-06-02

### Changed

- Opening a dfsu file is faster, because its element table is built with
  less work per element
  ([#20](https://github.com/DHI/mikecore-python/issues/20)).
- On Linux, importing mikecore appends its library folder to an existing
  `LD_LIBRARY_PATH` instead of replacing it.

## [0.2.0] - 2022-01-28

### Added

- `eumItem` and `eumUnit` entries from the MIKE 2022 EUM table: the items
  `eumIThermalConductivity`, `eumIDirectionalVariance` and
  `eumISpecificDissipationRate`, and the units `eumUradiansquared`,
  `eumUWattPerMeterPerDegreeCelsius` and `eumUWattPerFeetPerDegreeFahrenheit`
  ([#19](https://github.com/DHI/mikecore-python/issues/19)).

### Changed

- The bundled native libraries are the MIKE Core Release 2022 versions
  (20.0) on Windows and Linux, previously Release 2021 (19.x)
  ([#19](https://github.com/DHI/mikecore-python/issues/19)).
- `DfsFile.ReadDfs0DataDouble` and `WriteDfs0DataDouble` use the native DFS
  library on Linux as well as Windows. `ReadDfs0DataDouble` adds the time
  axis start time offset to the times of an equidistant time axis
  ([#19](https://github.com/DHI/mikecore-python/issues/19)).

### Removed

- The separate `MIKECoreCUtil.dll` is no longer bundled on Windows. The DFS
  library itself now provides the bulk dfs0 read and write
  ([#19](https://github.com/DHI/mikecore-python/issues/19)).

## [0.1.4] - 2021-12-01

### Added

- `DfsuFile` reads dfsu spectral files: point spectra (`DfsuSpectral0D`),
  line spectra (`DfsuSpectral1D`) and area spectra (`DfsuSpectral2D`), with
  their `Frequencies` and `Directions`, `NumberOfFrequencies`,
  `NumberOfDirections` and `IsSpectral`. A 1D dfsu file without layers is
  `Dfsu1D`
  ([#17](https://github.com/DHI/mikecore-python/issues/17)).

### Changed

- The numeric values of `DfsuFileType` members changed to make room for
  `Dfsu1D` (1) and the spectral types. Code that compares the type with
  its member names is unaffected
  ([#17](https://github.com/DHI/mikecore-python/issues/17)).

## [0.1.3] - 2021-11-08

### Fixed

- Reading and writing the encoding key of a compressed dfs file, which most
  dfs3 files are, works
  ([#14](https://github.com/DHI/mikecore-python/issues/14)).
- `MeshFile` reads a mesh with both triangles and quadrilaterals correctly.
  Triangles were read as quadrilaterals referring to a non-existent node 0
  ([#16](https://github.com/DHI/mikecore-python/issues/16)).

## [0.1.2] - 2021-08-25

### Added

- `DfsFile.ReadDfs0DataDouble` and `DfsFile.WriteDfs0DataDouble` read and
  write all times and item values of a dfs0 file as one array, with the
  times in the first column. `ReadDfs0DataDouble` can read selected items
  only. `WriteDfs0DataDouble` returns 0 on success
  ([#9](https://github.com/DHI/mikecore-python/issues/9),
  [#12](https://github.com/DHI/mikecore-python/issues/12)).
- `DfsTemporalAxis.ToSeconds` and `ToRelativeTime` convert between the time
  axis unit and seconds.

### Changed

- Setting a temporal axis property, such as `StartDateTime` or `TimeStep`, on
  a file opened for editing updates the file header
  ([#10](https://github.com/DHI/mikecore-python/issues/10)).
- In a file opened for editing, a custom block's `Values` changed in place
  are written to the file.
- One wheel holds the native libraries for both Windows and Linux.

### Removed

- `Dfs0Util`. Use `DfsFile.ReadDfs0DataDouble` instead.

### Fixed

- `TimeStepInSeconds` works for time units other than seconds instead of
  raising.

## [0.1.0] - 2021-05-26

### Added

- Initial release: Python access to the MIKE Core libraries, with an API
  close to the MIKE Core .NET API. It reads and writes dfs0, dfs1, dfs2,
  dfs3 and dfsu files (`DfsFile`, `DfsBuilder`, `DfsuFile`, `DfsuBuilder`),
  reads and writes mesh files (`MeshFile`, `MeshBuilder`), and gives access
  to EUM (`eum`) and map projections (`Projections`). It bundles the MIKE
  Core Release 2021 native libraries for 64-bit Python on Windows and Linux.

[Unreleased]: https://github.com/DHI/mikecore-python/compare/v0.2.2...HEAD
[0.2.2]: https://github.com/DHI/mikecore-python/compare/bbac3753d40a42c9840edea6ddcadd8512aeb883...v0.2.2
[0.2.1]: https://github.com/DHI/mikecore-python/compare/04c36b1ee3dc6c81905d75ff8c39d7b8a8411bd7...bbac3753d40a42c9840edea6ddcadd8512aeb883
[0.2.0]: https://github.com/DHI/mikecore-python/compare/a5e1b129315950c63b1efd91465f5e71ea97e091...04c36b1ee3dc6c81905d75ff8c39d7b8a8411bd7
[0.1.4]: https://github.com/DHI/mikecore-python/compare/fff099e2190dacb1a2906ad82c2094afa521b4f5...a5e1b129315950c63b1efd91465f5e71ea97e091
[0.1.3]: https://github.com/DHI/mikecore-python/compare/fc74acd85fa186f51816c0ce42d258487161e346...fff099e2190dacb1a2906ad82c2094afa521b4f5
[0.1.2]: https://github.com/DHI/mikecore-python/compare/v0.1.0...fc74acd85fa186f51816c0ce42d258487161e346
[0.1.0]: https://github.com/DHI/mikecore-python/releases/tag/v0.1.0
