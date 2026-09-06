# Roadmap

## Phase 0 — Foundation

Completed foundation: project structure, React/FastAPI applications, PostgreSQL Compose configuration, SQLAlchemy/Alembic setup, health endpoint, frontend connectivity check, tests, and documentation.

## Phase 1 — Profile

Completed: local user/profile schema and migration, profile read/update API, frontend Profile page, validation, tests, and documentation. Authentication is deliberately not included; the current local-owner placeholder will be replaced in Phase 9.

## Phase 2 — Weight Tracking

Completed: canonical-kilogram Weight Record schema and migration, local-owner CRUD API, kg/lb conversion, latest record lookup by measurement timestamp, frontend Weight page, tests, and PostgreSQL Compose verification. This phase tracks data only; charts, analytics, weight-loss recommendations, and medical guidance are not implemented.

## Phase 3 — Goals

Completed: target-weight Goal schema and migration, canonical kg conversion, manual status handling, local-owner CRUD API, Goals page, tests, and PostgreSQL verification. No automatic completion, recommendation, or analytics behavior is implemented.

## Phase 4 — Food Tracking

Completed: manual Meal and Meal Item schema and migration, local-owner CRUD API, entered quantity units, optional nutrition values, Meals page, tests, and PostgreSQL verification. Nutrition is tracking-only: no calorie targets, macro targets, food database, dieting, fasting, recommendation, or analytics behavior is implemented.

## Next phases

1. Phase 5 — Water / Activity / Sleep
2. Phase 6 — Habits
3. Phase 7 — Dashboard
4. Phase 8 — Analytics
5. Phase 9 — AI assistant with strict non-diagnostic safety boundaries
6. Phase 10 — Authentication and privacy
7. Phase 11 — Production hardening

Each phase requires its own reviewed data model, migration, API contract, UI, tests, and documentation updates. No calorie restriction, fasting system, aggressive weight-loss mechanics, diagnosis, prescription, or treatment guidance is planned.
