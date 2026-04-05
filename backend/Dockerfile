# ---- Stage 1: Builder ----
FROM python:3.10-slim AS builder

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Ensure dependencies are synced with CPU-only wheels (configured in pyproject.toml)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


# ---- Stage 2: Runtime ----
FROM python:3.10-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Activate venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy project files
COPY . .

# Create required directories
RUN mkdir -p documents chroma_db

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]