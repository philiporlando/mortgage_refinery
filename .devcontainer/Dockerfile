# Development Dockerfile (with dev tools)
FROM python:3.13-slim-trixie

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    bash \
    fontconfig \
    gzip \
    tar \
    && rm -rf /var/lib/apt/lists/*

# Install Starship
RUN curl -fsSL https://starship.rs/install.sh | sh -s -- -y
RUN echo 'eval "$(starship init bash)"' >> /root/.bashrc


# Install uv
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh

ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /workspace