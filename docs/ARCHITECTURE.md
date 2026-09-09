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
- Alembic owns schema version history. `users.id` remains the ownership identity, while Phase 9 adds email/password credentials and server-side sessions. A request dependency resolves the authenticated user from the opaque HttpOnly-cookie token; no router or service selects the first user in the database.
- Weight records, goals, meals, exercise sessions, dashboard, analytics, reminders, and today's notifications receive that authenticated user through Router → Service and filter ownership by `user_id` at repository level. Meal Items are accessed only through an owned Meal.
- Future domain modules must add models, a migration, schemas, repository/service behavior, API routes, tests, and documentation together.
- Authentication, AI, and other health-recording domain functions are future phases; implemented Analytics remains descriptive and read-only.

## Dashboard

Dashboard is a read-only composition service over existing user-scoped records; it adds no model or table. It uses the Profile IANA timezone for local-day boundaries, falling back to UTC, converts those boundaries to UTC for timestamp queries, and returns direct sums only.

## Analytics

Analytics is a read-only service over existing records. It groups 7d and 30d local calendar days through the Profile timezone (UTC fallback), converts boundaries to UTC queries, and adds no persistence or migration. It returns the latest Weight per day, direct nutrition values with explicit missing-item metadata, and Exercise duration/canonical-km/manual-calorie totals with activity breakdowns.

## Reminders

Reminders follow Router → Service → Repository and persist user-owned schedules. `GET /notifications/today` evaluates enabled daily/weekly schedules only when requested, using Profile timezone or UTC fallback. Local wall-clock `reminder_time` remains a database `TIME`, not a UTC timestamp. There are no occurrence rows, background jobs, push, email, SMS, or external delivery providers.

## Authentication

`/auth/login`, `/auth/logout`, and `/auth/me` use a server-side opaque-session design. Passwords are hashed with Argon2 through a maintained library. Only a random session token is placed in an HttpOnly, SameSite cookie; PostgreSQL stores its SHA-256 hash, expiry, and revocation state. The React auth provider reads current-user state, protects application routes, and centrally resets to sign-in after a `401`.

## Deployment boundary

The production-like frontend is a multi-stage Node build followed by nginx, not the Vite development server. Nginx serves SPA fallbacks for direct routes and proxies `/api/` to the backend, so the browser uses a same-origin cookie/API path. Compose treats Alembic as authoritative through a one-off `migrate` service that must complete after PostgreSQL is healthy before the backend starts. Backend and frontend health checks use `/api/v1/ready` and nginx HTTP availability respectively; the nginx probe uses `127.0.0.1` because the supplied server listener is IPv4.

Phase 9C verified this boundary in an isolated Compose project using a fresh PostgreSQL volume: migrations reached `0007_authentication`, authenticated user-owned Profile/Weight/Goal/Meal/Exercise/Reminder data flowed through nginx, cross-user reads were denied, direct SPA routes resolved, and a disposable backup restored successfully. The isolated resources and synthetic data are removed after verification. This is a deployment-path verification, not a public-production deployment claim.
