FROM python:3.12.5-slim

RUN apt-get update -y && apt-get install -y curl unzip patchelf
RUN curl -o bin.zip https://globalcdn.nuget.org/packages/dhi.mikecore.linux.ubuntu.22.1.0.nupkg && \
    unzip bin.zip && \
    mkdir -p /tmp/mikecore/bin/linux && \
    cp -r runtimes/linux-x64/native/* /tmp/mikecore/bin/linux

RUN pip install pytest

RUN patchelf --set-rpath '$ORIGIN' /tmp/mikecore/bin/linux/libufs.so && \
    patchelf --set-rpath '$ORIGIN' /tmp/mikecore/bin/linux/libeum.so && \
    patchelf --set-rpath '$ORIGIN' /tmp/mikecore/bin/linux/libMzCart.so && \
    patchelf --set-rpath '$ORIGIN' /tmp/mikecore/bin/linux/libpfs2004.so && \
    patchelf --set-rpath '$ORIGIN' /tmp/mikecore/bin/linux/libxerces-c-3.2.so

COPY . /tmp/

RUN pip install /tmp/.

COPY ./testdata /app/testdata
COPY ./tests /app/tests

WORKDIR /app
CMD pytest
