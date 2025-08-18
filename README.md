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


