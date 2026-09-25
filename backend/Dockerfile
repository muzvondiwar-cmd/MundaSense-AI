FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY requirements.txt pyproject.toml README.md ./
COPY src ./src
RUN python -m pip install --upgrade pip && \
    python -m pip install -r requirements.txt && \
    python -m pip install -e . --no-deps --no-build-isolation

COPY backend ./backend
COPY migrations ./migrations
COPY scripts ./scripts
COPY alembic.ini ./alembic.ini
COPY assets ./assets
COPY data/sample ./data/sample
COPY models ./models
COPY reports ./reports
COPY docs ./docs

EXPOSE 8000
CMD ["sh", "-c", "python -m alembic upgrade head && python scripts/seed_demo.py && python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"]
