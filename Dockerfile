# Multi-stage Dockerfile for Mermaid Render
# Supports development, production, and different deployment scenarios

# =============================================================================
# Base Stage - Common dependencies and setup
# =============================================================================
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Essential build tools
    build-essential \
    gcc \
    g++ \
    # Graphics and rendering dependencies
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf2.0-dev \
    libffi-dev \
    shared-mime-info \
    # Network and security
    ca-certificates \
    curl \
    wget \
    gnupg \
    # Git for VCS operations
    git \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Install UV for fast Python package management
RUN pip install uv

# Create non-root user for security
RUN groupadd -r mermaid && useradd -r -g mermaid -d /app -s /bin/bash mermaid

# Set working directory
WORKDIR /app

# =============================================================================
# Dependencies Stage - Install Python dependencies
# =============================================================================
FROM base as dependencies

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using UV
RUN uv sync --frozen --no-dev

# =============================================================================
# Development Stage - Full development environment
# =============================================================================
FROM dependencies as development

# Install development dependencies
RUN uv sync --frozen --all-extras

# Install additional development tools
RUN apt-get update && apt-get install -y \
    # Development tools
    vim \
    nano \
    htop \
    tree \
    # Browser dependencies for testing
    chromium \
    chromium-driver \
    # Node.js for Mermaid CLI (if needed)
    nodejs \
    npm \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright browsers for testing
RUN uv run playwright install chromium

# Copy source code
COPY . .

# Install package in development mode
RUN uv pip install -e .

# Set up development environment
RUN chown -R mermaid:mermaid /app
USER mermaid

# Expose ports for development server
EXPOSE 8000 8080

# Default command for development
CMD ["uv", "run", "python", "-m", "mermaid_render.interactive"]

# =============================================================================
# Testing Stage - Optimized for CI/CD testing
# =============================================================================
FROM dependencies as testing

# Install test dependencies
RUN uv sync --frozen --group test --group qa

# Copy source code
COPY . .

# Install package
RUN uv pip install .

# Run tests by default
CMD ["uv", "run", "pytest", "--cov=mermaid_render", "--cov-report=xml", "--cov-report=term"]

# =============================================================================
# Production Stage - Minimal production image
# =============================================================================
FROM base as production

# Copy only production dependencies
COPY --from=dependencies /app/.venv /app/.venv

# Copy source code
COPY mermaid_render ./mermaid_render
COPY pyproject.toml README.md LICENSE ./

# Install package
RUN uv pip install .

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/cache \
    && chown -R mermaid:mermaid /app

# Switch to non-root user
USER mermaid

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import mermaid_render; print('OK')" || exit 1

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "-m", "mermaid_render.cli", "--help"]

# =============================================================================
# Web Server Stage - Production web server
# =============================================================================
FROM production as webserver

# Install web server dependencies
RUN uv sync --frozen --group interactive

# Copy web assets if they exist
COPY --chown=mermaid:mermaid docs/static ./static/ 2>/dev/null || true

# Expose web server port
EXPOSE 8000

# Start web server
CMD ["uv", "run", "uvicorn", "mermaid_render.interactive.app:app", "--host", "0.0.0.0", "--port", "8000"]

# =============================================================================
# Documentation Stage - Documentation building and serving
# =============================================================================
FROM dependencies as docs

# Install documentation dependencies
RUN uv sync --frozen --group docs

# Copy documentation source
COPY docs ./docs
COPY mkdocs.yml ./
COPY README.md LICENSE CHANGELOG.md ./

# Copy source for API documentation
COPY mermaid_render ./mermaid_render

# Build documentation
RUN uv run mkdocs build

# Expose documentation port
EXPOSE 8080

# Serve documentation
CMD ["uv", "run", "mkdocs", "serve", "--dev-addr", "0.0.0.0:8080"]

# =============================================================================
# Build Stage - For building packages and distributions
# =============================================================================
FROM dependencies as builder

# Install build dependencies
RUN uv sync --frozen --group build

# Copy source code
COPY . .

# Build package
RUN uv run python -m build

# Create build artifacts directory
RUN mkdir -p /app/artifacts && cp dist/* /app/artifacts/

# =============================================================================
# Security Scanning Stage - For security analysis
# =============================================================================
FROM dependencies as security

# Install security tools
RUN uv sync --frozen --group security

# Copy source code
COPY . .

# Run security scans
CMD ["sh", "-c", "uv run safety check && uv run bandit -r mermaid_render/ && uv run pip-audit"]

# =============================================================================
# Multi-architecture support
# =============================================================================
# This Dockerfile supports multiple architectures:
# - linux/amd64 (x86_64)
# - linux/arm64 (ARM64/AArch64)
# - linux/arm/v7 (ARM32)

# Build arguments for multi-arch support
ARG TARGETPLATFORM
ARG BUILDPLATFORM
ARG TARGETARCH
ARG TARGETVARIANT

# Platform-specific optimizations can be added here if needed
# For example, different package installations for ARM vs x86

# =============================================================================
# Labels and Metadata
# =============================================================================
LABEL org.opencontainers.image.title="Mermaid Render"
LABEL org.opencontainers.image.description="A comprehensive Python library for generating Mermaid diagrams"
LABEL org.opencontainers.image.url="https://github.com/mermaid-render/mermaid-render"
LABEL org.opencontainers.image.source="https://github.com/mermaid-render/mermaid-render"
LABEL org.opencontainers.image.documentation="https://mermaid-render.readthedocs.io"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.vendor="Mermaid Render Team"
LABEL maintainer="Mermaid Render Team <contact@mermaid-render.dev>"

# Build information (will be set by CI/CD)
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION
LABEL org.opencontainers.image.created=$BUILD_DATE
LABEL org.opencontainers.image.revision=$VCS_REF
LABEL org.opencontainers.image.version=$VERSION
