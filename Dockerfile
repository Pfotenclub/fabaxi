# ==============================================================================
# Stage 1: Builder (installs git to build py-cord and creates virtual environment)
# ==============================================================================
FROM python:3.13-slim-bookworm AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ==============================================================================
# Stage 2: Hardened Stateless Runtime (Non-Root, Read-Only Root FS Ready)
# ==============================================================================
FROM python:3.13-slim-bookworm AS runtime

LABEL title="fabaxi"
LABEL authors="Wolfiii, Nicked"
LABEL version="2.0.0"

ENV TZ=Europe/Berlin \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    DOCKER=true \
    API_PORT=62299

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    groupadd -g 10001 fabaxi && \
    useradd -u 10001 -g 10001 -d /bot -s /sbin/nologin -M fabaxi

WORKDIR /bot

COPY --from=builder /opt/venv /opt/venv
COPY --chown=10001:10001 . /bot

USER 10001:10001

EXPOSE 62299

ENTRYPOINT ["python", "-u", "fabaxi.py"]
