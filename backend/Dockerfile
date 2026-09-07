FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app/backend
COPY backend/pyproject.toml ./pyproject.toml
COPY backend/requirements.lock ./requirements.lock
COPY backend/app ./app
RUN pip install --no-cache-dir --constraint requirements.lock .
COPY backend/alembic.ini ./alembic.ini
COPY database /app/database
RUN useradd --create-home --uid 10001 appuser

EXPOSE 8000
USER appuser
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
