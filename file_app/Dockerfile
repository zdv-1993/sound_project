FROM python:3.11-slim-buster

RUN pip install -U pip
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

ENV PYTHONPATH="$PYTHONPATH:/app"


COPY . /app

CMD python /app/server.py