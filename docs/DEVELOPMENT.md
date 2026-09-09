# Development

## Prerequisites

- Node.js 24+ and npm
- Python 3.12+
- Docker Desktop (recommended for PostgreSQL)

## Docker workflow

Copy `.env.example` to `.env`, choose a local password, then run:

```bash
docker compose up --build --force-recreate
```

Compose runs the dedicated `migrate` service before starting the API. The frontend is the production nginx image and proxies same-origin `/api/` requests to the backend. `--force-recreate` is the documented way to intentionally replace potentially stale containers after a source/image change; it does not remove volumes. Stop the stack with `docker compose down`; never use `docker compose down -v` for an existing database unless you explicitly intend to delete its data.

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

Vite development continues to use `VITE_API_BASE_URL=http://localhost:8000` from `.env`; the production Docker image builds with a relative API base so nginx serves `/api/v1/...` from the same origin.
