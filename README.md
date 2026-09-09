# Personal Health Tracking Application

A privacy-minded personal health tracking application. Phase 9 production hardening is complete: it adds password-based authentication, server-side sessions, and a production-like Docker deployment path. It does not provide medical advice.

## Technology

- Frontend: React, TypeScript, Vite, React Router, Vitest
- Backend: Python, FastAPI, Pydantic, SQLAlchemy, Alembic, Pytest
- Database: PostgreSQL 16

## Quick start with Docker

1. Copy `.env.example` to `.env` and replace the example password.
2. Start the stack:

   ```bash
   docker compose up --build --force-recreate
   ```

   Compose waits for PostgreSQL, runs the one-off `migrate` service, then starts the backend and production nginx frontend. This is an intentional rebuild command; it does not remove a database volume.

3. Open `http://localhost:5173`. The frontend proxies `/api/` to the backend on the Docker network. The API documentation is available at `http://localhost:8000/docs`.

The frontend displays the API health status and provides Profile, Weight, Goals, Meals, Exercise, Analytics, and Reminders pages at `/profile`, `/weight`, `/goals`, `/meals`, `/exercise`, `/analytics`, and `/reminders`.

## Local development

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for local setup, migration commands, and tests. Copy `.env.example` to `.env`; never commit that file.

After applying migrations, create or claim the single initial account through the interactive local-only command (it prompts for a password of at least 12 characters and does not expose it on the command line):

```bash
cd backend
python -m app.cli.bootstrap_user --email you@example.com
```

The application has no public sign-up endpoint. Sign in at `/login`; the browser keeps only an HttpOnly session cookie and the server stores a token hash.

## Project status

Phases 0–9 are implemented and verified. Phase 9 completed authentication and authorization, migration `0007_authentication`, production-like images, same-origin routing, liveness/readiness checks, and an isolated PostgreSQL/Docker end-to-end verification with a fresh migration chain, synthetic owned data, backup/restore, and cleanup. This verifies the repository's deployment path; it is not a claim that a public production environment has been deployed. Reminders are evaluated in-app when data is requested; push, email, SMS, and background delivery are not implemented.
