FROM tiangolo/uvicorn-gunicorn:python3.8-alpine3.10

COPY requirements.txt .
RUN apk add --no-cache gcc musl-dev zlib-dev jpeg-dev imagemagick-dev && \
    pip install --no-cache-dir -r requirements.txt && \    
    adduser -S app && \
    rm requirements.txt

USER app
COPY ./app /app
WORKDIR /app