FROM python:3.11-slim-buster

RUN pip install -U pip
RUN pip install "uvicorn[standard]" gunicorn

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
ENV PYTHONPATH=/app

COPY . /app

CMD ["uvicorn", "app:app", "--reload", "--host", "0.0.0.0", "--port", "60000", "--reload-dir", "/app"]
