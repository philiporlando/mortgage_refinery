# Development Dockerfile (with dev tools)
FROM python:3.13-slim-trixie

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -s /bin/bash vscode && \
    usermod -aG sudo vscode && \
    echo "vscode ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Install uv
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Add uv to path for all users
ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /workspace

# Switch to non-root user
USER vscode

# Set up Python environment
ENV PATH="/home/vscode/.local/bin:${PATH}"