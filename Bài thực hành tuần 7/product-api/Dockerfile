# ─── Stage 1: Builder ───
FROM python:3.12-slim AS builder

WORKDIR /build

COPY pyproject.toml ./
COPY src ./src

RUN python -m venv /opt/venv
ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# ─── Stage 2: Runtime ───
FROM python:3.12-slim

WORKDIR /app

RUN groupadd -r app && \
    useradd -r -g app -d /app app

COPY --from=builder --chown=app:app /opt/venv /opt/venv
COPY --chown=app:app src ./src
COPY --chown=app:app migrations ./migrations
COPY --chown=app:app wsgi.py ./wsgi.py

ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=wsgi

USER app

EXPOSE 5000

CMD ["sh", "-c", "flask --app wsgi db upgrade && exec gunicorn --bind 0.0.0.0:5000 'product_api.factory:create_app()'"]
