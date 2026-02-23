FROM python:3.12-slim

RUN pip install uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY src/ src/
COPY alembic/ alembic/
COPY alembic.ini .
COPY entrypoint.sh .

RUN adduser --disabled-password --no-create-home appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["./entrypoint.sh"]
