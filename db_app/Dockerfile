FROM python:3.11-slim-buster

RUN pip install -U pip
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
ENV PYTHONPATH=/app

COPY . /app

CMD uvicorn app.main:app --reload --host=0.0.0.0 --reload-dir /app