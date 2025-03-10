FROM python:3.12-alpine
LABEL maintainer="Yibing Wang"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY . /app
WORKDIR /app

# ARG will be overwritten by docker-compose
ARG DEV=false


RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install --upgrade setuptools && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
    then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    adduser \
    --disabled-password \
    --no-create-home \
    celery-worker-user

ENV PATH="/py/bin:$PATH"

USER celery-worker-user