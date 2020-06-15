FROM tiangolo/uvicorn-gunicorn:python3.8-alpine3.10

COPY requirements.txt .
RUN apk add --no-cache file gcc musl-dev curl tar file   zlib-dev jpeg-dev imagemagick imagemagick-dev tiff-dev  ffmpeg openjpeg-dev libpng-dev jasper-dev freetype-dev ffmpeg-dev  libvpx-dev  lame-dev speex-dev   fftw-dev lcms-dev  openexr-dev pango-dev perl-dev cairo && \
    pip install --no-cache-dir -r requirements.txt && \    
    adduser -S app && \
    rm requirements.txt



USER app
COPY ./app /app
WORKDIR /app