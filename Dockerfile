# syntax=docker/dockerfile:1
#
# Molecules & Models: render the Quarto site, then serve the static output with nginx.
# Railway builds this file (see railway.json) and routes traffic to $PORT.
#
#   docker build -t molmodels .
#   docker run --rm -p 8080:8080 molmodels                  # http://localhost:8080/
#
# The render executes every episode and lab from scratch (no _freeze), as CI does: allow 5-10 minutes.

ARG PYTHON_VERSION=3.12
ARG QUARTO_VERSION=1.10.20
ARG NGINX_VERSION=1.30


# --- Stage 1: render ---------------------------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim-trixie AS build
ARG QUARTO_VERSION
ARG TARGETARCH

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLBACKEND=Agg \
    QUARTO_PYTHON=/usr/local/bin/python

RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates curl \
 && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL "https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-${TARGETARCH:-amd64}.tar.gz" \
      | tar -xz -C /opt \
 && ln -s "/opt/quarto-${QUARTO_VERSION}/bin/quarto" /usr/local/bin/quarto \
 && quarto --version

# Same pins as Colab and local installs; a layer of its own so content edits do not reinstall it.
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

WORKDIR /site
COPY . .

# ESOL is not redistributed in the repository: download it with its SHA-256 check.
RUN python scripts/fetch_data.py

RUN rm -rf _freeze && quarto render


# --- Stage 2: serve ----------------------------------------------------------------------------
FROM nginx:${NGINX_VERSION}-alpine AS serve

# Railway sets PORT at runtime; the nginx entrypoint substitutes it into the template.
ENV PORT=8080

RUN rm -rf /usr/share/nginx/html/*
COPY docker/nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /site/_site /usr/share/nginx/html

EXPOSE 8080
