FROM tiangolo/uvicorn-gunicorn:python3.8-alpine3.10

LABEL maintainer="Sebastian Ramirez <tiangolo@gmail.com>"

RUN adduser -S app

USER app
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

COPY . .
    