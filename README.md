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


### Debian 9 *stretch*

See [Dockerfile](Dockerfile)

