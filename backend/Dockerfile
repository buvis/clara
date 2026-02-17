FROM python:3.12-slim

RUN pip install uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY src/ src/
COPY alembic/ alembic/
COPY alembic.ini .

CMD ["uv", "run", "uvicorn", "clara.main:app", "--host", "0.0.0.0", "--port", "8000"]
