FROM python:3.9.4-slim

RUN apt-get update -y && apt-get install curl -y && apt-get install unzip -y
RUN curl -o bin.zip https://globalcdn.nuget.org/packages/dhi.mikecore.linux.rhel7.20.0.0.nupkg && \
    unzip bin.zip && \
    mkdir -p /tmp/mikecore/bin/linux && \
    cp -r runtimes/linux-x64/native/* /tmp/mikecore/bin/linux

RUN pip install pytest numpy

ENV LD_LIBRARY_PATH=/usr/local/lib/python3.9/site-packages/mikecore/bin/linux

COPY . /tmp/

RUN pip install /tmp/.

COPY ./testdata /app/testdata
COPY ./tests /app/tests

WORKDIR /app
CMD pytest
