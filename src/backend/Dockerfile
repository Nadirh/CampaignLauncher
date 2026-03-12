FROM python:3.12-slim AS base

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Install Playwright Chromium and its system dependencies
RUN uv run playwright install --with-deps chromium

COPY app/ app/
COPY alembic.ini alembic.ini
COPY alembic/ alembic/

# Create non-root user and copy Playwright browser cache to its home
RUN groupadd --gid 1001 appuser && \
    useradd --uid 1001 --gid 1001 --create-home appuser && \
    mkdir -p /home/appuser/.cache && \
    cp -r /root/.cache/ms-playwright /home/appuser/.cache/ms-playwright && \
    chown -R appuser:appuser /app /home/appuser/.cache

USER appuser

EXPOSE 8000

CMD ["/bin/sh", "-c", "/app/.venv/bin/alembic upgrade head && /app/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000"]
