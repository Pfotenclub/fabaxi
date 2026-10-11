FROM python:3.13-slim-bookworm
LABEL title="fabaxi"
LABEL authors="Wolfiii, Nicked"
LABEL version="1.0.0"

WORKDIR /bot

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /bot

ENV DOCKER=true
ENV API_PORT=62299

VOLUME ["/db"]
EXPOSE 62299

ENTRYPOINT ["python", "fabaxi.py"]
