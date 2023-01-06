FROM python:3.11-slim-buster

RUN pip install -U pip
RUN pip install "uvicorn[standard]" gunicorn
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
ENV PYTHONPATH=/app

COPY . /app

#CMD uvicorn app.main:app --reload --host=0.0.0.0 --reload-dir /app
CMD gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000