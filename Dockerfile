FROM python:3.12.8-slim-bookworm
LABEL title="chatgpaint"
LABEL authors="Wolfiii, Nicked"
LABEL version="1.0.0"

COPY . /bot

WORKDIR /bot

RUN pip install -r requirements.txt
ENV DOCKER=true

VOLUME ["/db"]
EXPOSE 8000

ENTRYPOINT ["python", "bot.py"]