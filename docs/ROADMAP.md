# Roadmap

## Phase 0 — Foundation

Completed foundation: project structure, React/FastAPI applications, PostgreSQL Compose configuration, SQLAlchemy/Alembic setup, health endpoint, frontend connectivity check, tests, and documentation.

## Phase 1 — Profile

Completed: user/profile schema and migration, profile read/update API, frontend Profile page, validation, tests, and documentation. Phase 9 later adds authenticated ownership without changing the user UUID that owns existing records.

## Phase 2 — Weight Tracking

Completed: canonical-kilogram Weight Record schema and migration, local-owner CRUD API, kg/lb conversion, latest record lookup by measurement timestamp, frontend Weight page, tests, and PostgreSQL Compose verification. This phase tracks data only; charts, analytics, weight-loss recommendations, and medical guidance are not implemented.

## Phase 3 — Goals

Completed: target-weight Goal schema and migration, canonical kg conversion, manual status handling, local-owner CRUD API, Goals page, tests, and PostgreSQL verification. No automatic completion, recommendation, or analytics behavior is implemented.

## Phase 4 — Food Tracking

Completed: manual Meal and Meal Item schema and migration, local-owner CRUD API, entered quantity units, optional nutrition values, Meals page, tests, and PostgreSQL verification. Nutrition is tracking-only: no calorie targets, macro targets, food database, dieting, fasting, recommendation, or analytics behavior is implemented.

## Phase 5 — Exercise Tracking

Completed: manual Exercise Session schema and migration, local-owner CRUD API, canonical km storage with km/mi input conversion, optional manually entered calories, Exercise page, tests, and PostgreSQL verification. No exercise plans, automatic calorie estimates, pace analysis, analytics, or recommendations are implemented.

## Phase 6 — Dashboard

Completed: read-only Dashboard endpoint and Today page using Profile timezone-aware daily summaries. No migration, analytics, targets, trends, scoring, or recommendations are implemented.

## Phase 7 — Analytics

Implemented: descriptive 7/30-day weight, entered nutrition, and exercise summaries with local-calendar grouping.

## Phase 8 — Notifications & Reminders

Completed: local-user, in-app daily/weekly reminders with Profile-timezone due/upcoming evaluation, CRUD management, Today dashboard integration, automated tests, and PostgreSQL migration/smoke verification. No push, email, SMS, background worker, or delivery history is implemented.

## Next phases

1. Phase 9 — Production Hardening (in progress: 9A authentication/authorization and 9B deployment hardening complete locally; 9C isolated Docker/PostgreSQL verification pending)

Each phase requires its own reviewed data model, migration, API contract, UI, tests, and documentation updates. No calorie restriction, fasting system, aggressive weight-loss mechanics, diagnosis, prescription, or treatment guidance is planned.
