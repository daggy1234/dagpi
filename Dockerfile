FROM alpine:edge

COPY requirements.txt .

RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories \
    && apk add --no-cache python3 python3-dev py3-pip py3-wheel py3-setuptools py3-aiohttp py3-numpy-dev py3-pillow py3-scipy py3-matplotlib py3-pandas \
    && apk add --no-cache --virtual .build-deps gcc libc-dev make \
    && pip install https://ftp.travitia.xyz/uvloop-0.15.0.dev0-cp38-cp38-linux_x86_64.whl \
    && pip install https://ftp.travitia.xyz/scikit_image-0.18.dev0-cp38-cp38-linux_x86_64.whl \
    && pip install --no-cache-dir uvicorn gunicorn fastapi PyWavelets \
    && apk del .build-deps \
    && apk add --no-cache gcc musl-dev curl tar file   zlib-dev jpeg-dev imagemagick imagemagick-dev tiff-dev  ffmpeg openjpeg-dev libpng-dev openjpeg-dev freetype-dev ffmpeg-dev  libvpx-dev  lame-dev speex-dev   fftw-dev lcms-dev openexr-dev pango-dev perl-dev cairo g++ libstdc++ bash  \
    && pip install --no-cache-dir -r requirements.txt \
    && adduser -S app \
    && rm requirements.txt \
    && apk add --virtual .fetch curl \
    && curl https://raw.githubusercontent.com/tiangolo/uvicorn-gunicorn-docker/master/docker-images/start.sh -o start.sh \
    && chmod +x start.sh \
    && curl https://raw.githubusercontent.com/tiangolo/uvicorn-gunicorn-docker/master/docker-images/gunicorn_conf.py -o gunicorn_conf.py \
    && chmod +x gunicorn_conf.py \
    && curl https://raw.githubusercontent.com/tiangolo/uvicorn-gunicorn-docker/master/docker-images/start-reload.sh -o start-reload.sh \
    && chmod +x start-reload.sh \
    && apk del .fetch

USER app
COPY ./app /app
WORKDIR /app/

ENV PYTHONPATH=/app

EXPOSE 80
EXPOSE 443
CMD ["/start.sh"]