# FROM gcr.io/buildpacks/builder:latest
# FROM gcr.io/google-appengine/python
# FROM python:3.10-slim
FROM gcr.io/gae-runtimes/buildpacks/google-gae-22/python/builder
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
  libmagic1 \
  python3.11 && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . . 
RUN echo $PATH

# Hacky way to create Cloud Native Build user??
# Create cnb user and group
RUN groupadd -g 1000 cnb && \
    useradd -u 1000 -g cnb -m -s /bin/bash cnb

USER cnb
# USER madelaineboyd
# USER