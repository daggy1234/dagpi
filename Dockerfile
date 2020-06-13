FROM tiangolo/uvicorn-gunicorn:python3.8-alpine3.10

RUN adduser -S app

USER app
WORKDIR /app

COPY requirements.txt .
RUN apk add --virtual .build --no-cache gcc musl-dev && \
    pip install --no-cache-dir --user -r requirements.txt && \
    apk del .build

COPY . .