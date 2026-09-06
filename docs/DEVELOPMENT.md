# Development

## Prerequisites

- Node.js 24+ and npm
- Python 3.12+
- Docker Desktop (recommended for PostgreSQL)

## Docker workflow

Copy `.env.example` to `.env`, choose a local password, then run:

```bash
docker compose up --build
```

Compose runs migrations before starting the API. Stop the stack with `docker compose down`; use `docker compose down -v` only when you explicitly want to remove local database data.

## Local workflow

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Backend:

```bash
cd backend
python -m venv .venv
# Activate the environment using your shell's normal command.
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload
```

For a local backend outside Docker, set `DATABASE_URL` with host `localhost`, not `db`.
