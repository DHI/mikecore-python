from python:3.7.9-slim-stretch

RUN pip install pytest

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

ENV LD_LIBRARY_PATH=/app/bin/linux

COPY . /app

RUN pip install -e /app

WORKDIR /app
CMD pytest