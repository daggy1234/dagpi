FROM tiangolo/uvicorn-gunicorn:python3.8-alpine3.10

COPY requirements.txt .
RUN apk add --virtual .build --no-cache gcc musl-dev zlib-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del .build && \
    adduser -S app && \
    rm requirements.txt

USER app
WORKDIR /app
COPY . .