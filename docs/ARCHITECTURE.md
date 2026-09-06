# Architecture

## Current overview

```text
React + TypeScript (Vite)
          |
          | REST /api/v1
          v
FastAPI router -> service -> repository -> SQLAlchemy -> PostgreSQL
```

The frontend is a standalone single-page application. `src/services` owns HTTP calls, features own UI behavior, and pages compose features. The backend uses a deliberately small layered structure: routers own HTTP concerns, services coordinate business behavior, and repositories execute data access.

`GET /api/v1/health` checks database connectivity through this full backend path. Profile, Weight Record, Goal, Meal, and Exercise modules follow the same path. Unit conversion is centralized in backend services and frontend utilities rather than duplicated across UI components. Meal lists load their Meal Items with `selectinload`, avoiding per-meal item queries.

## Boundaries

- PostgreSQL is the production and Docker development datastore.
- Alembic owns schema version history. Phase 1 introduces one local `users` record and its one-to-one `user_profiles` record. The temporary single-user selection belongs only to the pre-authentication phase; authentication will replace it with an authenticated owner lookup.
- Weight records, goals, meals, and exercise sessions use the local owner lookup and are filtered by `user_id` at repository level. Meal Items are accessed only through a Meal owned by that local user. Authentication will replace the lookup without changing these ownership relations.
- Future domain modules must add models, a migration, schemas, repository/service behavior, API routes, tests, and documentation together.
- Authentication, AI, and other health-recording domain functions are future phases; implemented Analytics remains descriptive and read-only.

## Dashboard

Dashboard is a read-only composition service over existing user-scoped records; it adds no model or table. It uses the Profile IANA timezone for local-day boundaries, falling back to UTC, converts those boundaries to UTC for timestamp queries, and returns direct sums only.

## Analytics

Analytics is a read-only service over existing records. It groups 7d and 30d local calendar days through the Profile timezone (UTC fallback), converts boundaries to UTC queries, and adds no persistence or migration. It returns the latest Weight per day, direct nutrition values with explicit missing-item metadata, and Exercise duration/canonical-km/manual-calorie totals with activity breakdowns.
