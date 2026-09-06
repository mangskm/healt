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

## Engineering rules

- Use TypeScript and component-based React UI.
- Use Pydantic models at API boundaries and keep business logic out of routers.
- Add or update tests for meaningful behavior changes.
- Do not hard-code credentials, tokens, or personal health data. Keep local values in `.env`; maintain `.env.example`.
- Update the relevant Markdown documentation when APIs, architecture, schema, or development workflows change.

## Health-safety boundaries

- Do not build features that diagnose illness, prescribe treatment, promote dangerous calorie restriction/fasting, or encourage rapid weight loss or over-exercise.
- Any future AI functionality must be informational, general, and clearly non-diagnostic.
