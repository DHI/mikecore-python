# MIKE Core for Python

A project to facilitate use of the MIKE Core components with Python, targeting as
well Windows as Linux. 

The MIKE Core Python classes have an API which is almost identical to the MIKE Core .NET API, to the extend possible. 
Since Python does not support all the language constructions that .NET/C\# does (as e.g. method overriding),
the API's are not completely identical. Also, the number of classes in the Python version is also smaller, 
since Python classes can be formed while being used. However, the examples and documentation for the 
.NET/C\# API is to a high degree applicable also for the use of MIKE Core Python. For details, visit:

[MIKE for Developers/MIKE Core](http://docs.mikepoweredbydhi.com/core_libraries/core-libraries/)

This package is also intended for bringing
[MIKE IO on Linux](https://github.com/DHI/mikeio/issues/50). 

## Installation

Once published on PyPI...

```pip install mikecore```


## Testing on Linux using Docker

1. `git clone https://github.com/DHI/mikecore-python`
2. `cd mikecore-python`
2. `docker build . -t mikecore:latest`
3. `docker run mikecore:latest`

Then you should get output like this:
```
============================= test session starts ==============================
platform linux -- Python 3.9.4, pytest-6.2.4, py-1.10.0, pluggy-0.13.1
rootdir: /app
collected 68 items

tests/test_dfs0.py ........                                              [ 11%]
tests/test_dfs2.py ..........                                            [ 26%]
tests/test_dfs_basic.py .....                                            [ 33%]
tests/test_dfs_custom_block.py ..                                        [ 36%]
tests/test_dfs_static_item.py .                                          [ 38%]
tests/test_dfsbuilder.py ......                                          [ 47%]
tests/test_dfsu2D.py ..........                                          [ 61%]
tests/test_dfsu_file.py ..........                                       [ 76%]
tests/test_eum.py ..                                                     [ 79%]
tests/test_mesh.py ...                                                   [ 83%]
tests/test_miketools.py .                                                [ 85%]
tests/test_projections.py ..........                                     [100%]

============================= 68 passed in 31.46s ==============================
```


