FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

WORKDIR /opt/render/project/src

COPY app/backend /opt/render/project/src/app/backend
COPY app/shared /opt/render/project/src/app/shared

RUN pip install --upgrade pip && \
    pip install -e "/opt/render/project/src/app/backend[ml]" && \
    mkdir -p /opt/render/project/src/app/backend/data

WORKDIR /opt/render/project/src/app/backend

EXPOSE 8000

CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
