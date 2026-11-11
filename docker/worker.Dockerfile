FROM mcr.microsoft.com/playwright/python:v1.49.0-noble AS base
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PROJECT_ENVIRONMENT=/opt/venv PATH="/opt/venv/bin:$PATH"
WORKDIR /app/api
COPY api/pyproject.toml api/uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

FROM base AS dev
RUN uv sync --frozen --no-install-project
USER pwuser
CMD ["python", "-m", "receipts.worker"]

FROM base AS prod
COPY api/ ./
RUN uv sync --frozen --no-dev
USER pwuser
CMD ["python", "-m", "receipts.worker"]
