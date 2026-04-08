# --- Build stage ---
FROM python:3.12-slim AS builder

WORKDIR /app
COPY . .
RUN python archive-index/build-index.py

# --- Runtime stage ---
FROM python:3.12-slim

LABEL org.opencontainers.image.source="https://github.com/AiFeatures/system_prompts_leaks"
LABEL org.opencontainers.image.description="System prompt archive with searchable index"

RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid 1000 --create-home appuser

WORKDIR /app
COPY --from=builder --chown=appuser:appuser /app .

USER appuser

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD ["python", "-c", "import json, pathlib; idx=json.loads(pathlib.Path('/app/archive-index/index.json').read_text()); assert idx['count']>0"]

ENTRYPOINT ["python", "archive-index/build-index.py"]
