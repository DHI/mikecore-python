import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mikecore",
    version="0.1.4",
    install_requires=["numpy"],
    author="DHI",
    author_email="mike@dhigroup.com",
    description="MIKE Core contains core libraries, like DFS (Data File System), EUM and more.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DHI/mikecore-python",
    packages=setuptools.find_packages(),
    license="BSD-3",
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.5<",
    include_package_data=True,
)
