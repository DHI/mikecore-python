# MIKE Core for Python

A project to facilitate use of the MIKE Core components with Python, targeting Windows as
well as Linux. 

The MIKE Core Python classes have an API which is almost identical to the MIKE Core .NET API, to the extend possible. 
Since Python does not support all the language constructions that .NET/C\# does (as e.g. method overriding),
the API's are not completely identical. Also, the number of classes in the Python version is also smaller, 
since Python classes can be formed while being used. However, the examples and documentation for the 
.NET/C\# API is to a high degree applicable also for the use of MIKE Core Python. For details, visit:

[MIKE for Developers/MIKE Core](http://docs.mikepoweredbydhi.com/core_libraries/core-libraries/)

This library is the foundation for [MIKE IO](https://github.com/DHI/mikeio). 

## Installation

```pip install mikecore```

### Using mikecore alongside a MIKE installation (Linux)

mikecore always uses the MIKE Core libraries bundled with it (renamed to
`lib*-mikecore.so`), even when a MIKE installation's `bin` is on
`LD_LIBRARY_PATH`, for example after sourcing `mikevars.sh`. Importing mikecore
doesn't change `LD_LIBRARY_PATH`, so MIKE programs started from Python use the
installation's own libraries.

A MIKE engine, or an engine-based Python library, can run in the same process
as mikecore, but each side uses its own copy of the MIKE Core libraries. The
copies don't share state: handles, pointers or settings (such as loaded EUM
definitions) from one can't be passed to the other. Exchange data through files
instead. Putting mikecore's `bin` folder first on `LD_LIBRARY_PATH` isn't needed
anymore, and no longer makes the engine use mikecore's libraries.

mikecore's libraries don't use OpenMP, so its bundled OpenMP runtime
(`libiomp5`) never starts and doesn't conflict with an engine's.

### Using a MIKE installation's libraries (Linux and Windows)

To share one set of MIKE Core libraries with an engine instead, or to check
whether mikecore works with a MIKE installation, set `MIKECORE_PYTHON_BIN` to the
installation's `bin` folder before importing mikecore:

```bash
MIKECORE_PYTHON_BIN=/path/to/MIKE/bin python -c "import mikecore; print(mikecore.mikebin)"
MIKECORE_PYTHON_BIN=/path/to/MIKE/bin uv run pytest   # smoke-test mikecore against that installation
```

On Windows (PowerShell), point it at the installation's `bin\x64` folder:

```powershell
$env:MIKECORE_PYTHON_BIN = "C:\path\to\MIKE\bin\x64"
python -c "import mikecore; print(mikecore.mikebin)"
```

mikecore then loads the installation's libraries and `EUM.xml` instead of its own.
This is at your own risk: mikecore is only tested with its bundled libraries, and
an installation's release may not match mikecore's API or EUM definitions.

## Development

All commands are run from the project root.

1.  **Sync & Build**
    ```bash
    uv sync
    # Use 'uv sync --reinstall' to force-rebuild native components.
    ```

2.  **Update EUM Types** (for new release, or whenever EUM.xml changes)
    ```bash
    # Generate definitions from the new native build
    uv run ./buildUtil/eumXMLProcess.py > eumItemUnit.txt

    # Use a diff tool to merge changes into mikecore/eum.py.
    ```

3.  **Run Tests**
    ```bash
    uv run pytest
    ```

4.  **Build Packages** (Optional)
    ```bash
    uv build
    ```


