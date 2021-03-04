import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mikecore",
    version="0.0.1",
    install_requires=["numpy"],
    author="DHI",
    author_email="mike@dhigroup.com",
    description="MIKE Core contains core libraries, like DFS (Data File System), EUM and more.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD-3-Clause License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.5<",
)
