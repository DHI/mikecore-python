FROM ubuntu

RUN apt-get update -y

RUN apt-get install python3-pip

RUN pip3 install pytest

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

ENV LD_LIBRARY_PATH=/app/bin/linux

COPY . /app

RUN pip install -e /app

WORKDIR /app
CMD pytest