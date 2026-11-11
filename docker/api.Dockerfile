FROM python:3.12-slim AS base
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PROJECT_ENVIRONMENT=/opt/venv PATH="/opt/venv/bin:$PATH"
WORKDIR /app/api
COPY api/pyproject.toml api/uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

FROM base AS dev
RUN uv sync --frozen --no-install-project
RUN useradd --create-home app && mkdir -p /app/data && chown -R app /app
USER app
CMD ["sh", "-c", "uvicorn receipts.main:app --host 0.0.0.0 --port 8000 --reload"]

FROM base AS prod
COPY api/ ./
RUN uv sync --frozen --no-dev
RUN useradd --create-home app && mkdir -p /app/data && chown -R app /app
USER app
CMD ["sh", "-c", "uvicorn receipts.main:app --host 0.0.0.0 --port 8000"]
