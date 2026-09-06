# Personal Health Tracking Application

A privacy-minded personal health tracking application. Phase 6 adds a read-only Dashboard. It does not provide medical advice.

## Technology

- Frontend: React, TypeScript, Vite, React Router, Vitest
- Backend: Python, FastAPI, Pydantic, SQLAlchemy, Alembic, Pytest
- Database: PostgreSQL 16

## Quick start with Docker

1. Copy `.env.example` to `.env` and replace the example password.
2. Start the stack:

   ```bash
   docker compose up --build
   ```

3. Open `http://localhost:5173`. The API documentation is available at `http://localhost:8000/docs`.

The frontend displays the API health status and provides Profile, Weight, Goals, Meals, and Exercise pages at `/profile`, `/weight`, `/goals`, `/meals`, and `/exercise`.

## Local development

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for local setup, migration commands, and tests. Copy `.env.example` to `.env`; never commit that file.

## Project status

Phases 0–6 are implemented. Planned health-recording features are listed in [docs/ROADMAP.md](docs/ROADMAP.md).
