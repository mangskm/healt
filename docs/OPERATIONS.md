# Operations

## Deployment modes

Development may run Vite on `localhost:5173` and FastAPI on `localhost:8000`; Vite uses `VITE_API_BASE_URL=http://localhost:8000`. The production-like Compose stack builds React assets once, serves them through nginx, and proxies same-origin `/api/` requests to the backend. It runs a one-off Alembic `migrate` service after PostgreSQL readiness and before the backend.

Credentialed CORS origins are an explicit configuration list and cannot use `*`. Configure `TRUSTED_HOSTS` for the deployment hostnames. Session cookies are HttpOnly, SameSite `Lax`, path `/`, expire according to `SESSION_TTL_MINUTES`, and default to `Secure` when `APP_ENV=production`; HTTPS termination and protected networks remain deployment responsibilities.

Use `docker compose up --build --force-recreate` to intentionally replace containers with current source-derived images. This does not remove data volumes. Never use `docker compose down -v`, remove volumes, or reset a database merely to troubleshoot an image.

The frontend healthcheck probes `http://127.0.0.1:8080/` inside nginx. The server configuration listens on IPv4, so using `localhost` may resolve to IPv6 in Alpine and report a false unhealthy state. Phase 9C verified the complete stack with a separately named Compose project, alternate host ports, and a fresh PostgreSQL volume. Use that isolation pattern for destructive verification cleanup; never direct it at a main or production project.

## Back up and restore

Backups contain personal health data. Store them in encrypted, access-controlled storage and never commit them. Obtain database credentials through the environment or a secure prompt; do not put passwords in command history or documentation.

To back up a running Compose database, run `pg_dump` inside the database container and redirect the resulting custom-format dump to a protected local path. The container receives its credentials through its environment; this command does not put a password on the command line:

```powershell
docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > protected-backup.dump
```

Restore only into a new, disposable database/container with `pg_restore`, then set `DATABASE_URL` to that disposable target, run `alembic upgrade head`, and verify `/api/v1/ready`. Do not restore over the main database or use a backup workflow as a reason to drop an existing database.

## Windows port troubleshooting

Before stopping anything, identify the owner of the port:

```powershell
Get-NetTCPConnection -LocalPort 5173,8000,5432 -ErrorAction SilentlyContinue
Get-CimInstance Win32_Process -Filter "ProcessId = <pid>"
docker ps
```

A local Uvicorn process and a Docker backend can both contend for port 8000. Inspect the owning process/container and stop only the specifically identified application. Never blindly terminate Docker Desktop backend processes, `com.docker.backend.exe`, or `wslrelay.exe`.
