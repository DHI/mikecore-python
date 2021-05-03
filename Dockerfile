FROM python:3.9.4-buster-slim

RUN pip install pytest numpy

ENV LD_LIBRARY_PATH=/usr/local/lib/python3.9/site-packages/mikecore/bin/linux

COPY . /tmp/

RUN pip install /tmp/.

COPY ./testdata /app/testdata
COPY ./tests /app/tests

WORKDIR /app
CMD pytest