FROM python:3.12.5-slim

# define variable version
ARG VERSION=22.1.0

RUN apt-get update -y && apt-get install -y curl unzip patchelf
RUN curl -o bin.zip https://globalcdn.nuget.org/packages/dhi.mikecore.linux.ubuntu.$VERSION.nupkg && \
    unzip bin.zip && \
    mkdir -p /app/mikecore/bin/linux && \
    cp -r runtimes/linux-x64/native/* /app/mikecore/bin/linux

RUN curl -o dfs.zip https://globalcdn.nuget.org/packages/dhi.dfs.$VERSION.nupkg && \
    unzip -o dfs.zip && \
    mkdir -p /app/mikecore/bin/windows && \
    cp -r runtimes/win-x64/native/* /app/mikecore/bin/windows

RUN curl -o projections.zip https://globalcdn.nuget.org/packages/dhi.projections.$VERSION.nupkg && \
    unzip -o projections.zip && \
    cp -r runtimes/win-x64/native/* /app/mikecore/bin/windows

# DHI.EUM
RUN curl -o eum.zip https://globalcdn.nuget.org/packages/dhi.eum.$VERSION.nupkg && \
    unzip -o eum.zip && \
    cp -r runtimes/win-x64/native/* /app/mikecore/bin/windows

# DHI.DHIfl
RUN curl -o dhifl.zip https://globalcdn.nuget.org/packages/dhi.dhifl.$VERSION.nupkg && \
    unzip -o dhifl.zip && \
    cp -r runtimes/win-x64/native/* /app/mikecore/bin/windows

RUN pip install pytest setuptools twine wheel

RUN patchelf --set-rpath '$ORIGIN' /app/mikecore/bin/linux/libufs.so && \
    patchelf --set-rpath '$ORIGIN' /app/mikecore/bin/linux/libeum.so && \
    patchelf --set-rpath '$ORIGIN' /app/mikecore/bin/linux/libMzCart.so && \
    patchelf --set-rpath '$ORIGIN' /app/mikecore/bin/linux/libpfs2004.so && \
    patchelf --set-rpath '$ORIGIN' /app/mikecore/bin/linux/libxerces-c-3.2.so

WORKDIR /app

COPY . /app

RUN pip install .

RUN pytest

# build python package
RUN python setup.py bdist_wheel

# get the wheel file to the host (for example)
# podman build -t mikecore .
# podman run -it --rm -t -v /tmp:/tmp mikecore bash
# cp dist/mikecore-0.3.0-py3-none-any.whl /tmp