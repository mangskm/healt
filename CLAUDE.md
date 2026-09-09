# Project Instructions

## Scope and workflow

- Work one development phase at a time. Do not implement later phases early.
- Before changing code, inspect the affected files and relevant documentation.
- For substantial work, state assumptions, plan, affected files, implementation, tests, and documentation updates.
- Preserve existing behavior unless a change is intentional and documented.

## Architecture

- The frontend calls versioned REST endpoints under `/api/v1`.
- Backend flow is API router -> service -> repository -> SQLAlchemy/PostgreSQL.
- Keep request/response models in `app/schemas`, persistence models in `app/models`, and database access in `app/repositories`.
- Database schema changes require an Alembic migration. Do not use `create_all` as application startup migration logic.
- When an input supports multiple units, store one documented canonical value and keep conversion logic in a shared service or utility.
- Meal Items retain the entered quantity and unit; do not add conversion, nutrition-target, or recommendation logic without a separately approved phase.
- Exercise distance is stored canonically in kilometers; manual calorie-burn values must never be estimated by the application.
- Dashboard is read-only composition. Its “today” range uses the Profile IANA timezone, falling back to UTC, and must not introduce analytics or recommendations.
- Analytics is also read-only: use Profile timezone/UTC fallback, direct historical aggregates, and no recommendations or predictions.
- Reminders are user-managed in-app schedules. Interpret their stored local `TIME` through the Profile timezone (UTC fallback); never add background delivery, external notification providers, or inferred/medical reminders in this phase.
- Authentication is server-side opaque-session authentication. Resolve the current user with the request dependency, never by selecting the first database user. Password hashes use Argon2 through the established library; raw passwords and raw session tokens must never be logged, stored, or returned in JSON.
- The initial account is created or claimed only through `python -m app.cli.bootstrap_user`; do not add a public claim or signup endpoint without a separately approved scope.
- Docker Compose uses a one-off Alembic `migrate` service before backend startup. The production-like frontend is nginx with a same-origin `/api/` proxy; do not revert it to a Vite dev server for deployment.
- The nginx container healthcheck must probe the configured IPv4 listener (`127.0.0.1`), not an ambiguous `localhost` IPv6 resolution. Keep deployment verification isolated from any main database or Compose project.
- Keep credentialed CORS origin lists explicit (never `*`), use trusted-host configuration, and log only method/path/status/duration—never request bodies, cookies, passwords, tokens, or database URLs.
- Post-roadmap UI work must preserve existing API contracts and authenticated routing. Use the shared application shell, tokens, confirmation dialog, and status feedback instead of reintroducing page-specific visual patterns.

## Engineering rules

- Use TypeScript and component-based React UI.
- Use Pydantic models at API boundaries and keep business logic out of routers.
- Add or update tests for meaningful behavior changes.
- Do not hard-code credentials, tokens, or personal health data. Keep local values in `.env`; maintain `.env.example`.
- Update the relevant Markdown documentation when APIs, architecture, schema, or development workflows change.

## Health-safety boundaries

- Do not build features that diagnose illness, prescribe treatment, promote dangerous calorie restriction/fasting, or encourage rapid weight loss or over-exercise.
- Any future AI functionality must be informational, general, and clearly non-diagnostic.
