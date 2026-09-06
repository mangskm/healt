# Testing

## Backend

Backend tests use Pytest and FastAPI's `TestClient`. The test database substitutes in-memory SQLite, so it verifies health, Profile, Weight Record, Goal, Meal, Meal Item, Exercise Session, and Dashboard aggregation behavior, including UTC fallback and Profile-timezone day boundaries.

```bash
cd backend
pytest
```

Database-specific migrations and PostgreSQL behavior are verified through the Compose stack. Phase 8 applies `0006_notifications`, checks the Alembic head and health endpoint, then runs a synthetic reminder CRUD/today-notification smoke test and cleans up its test data.

## Frontend

Frontend component tests use Vitest, jsdom, and Testing Library.

```bash
cd frontend
npm test
npm run build
```

Frontend tests cover the health indicator, Profile save flow, Weight behavior, Goals empty/create/validation behavior, Meals behavior, Exercise empty/history/create/delete/edit behavior, distance conversion, meal totals, and kg/lb conversion.

Dashboard verification covers empty states plus backend timezone/day-boundary and direct-sum behavior. PostgreSQL smoke testing uses only synthetic records and restores the Profile after use.

Analytics tests cover local-day period boundaries, latest-weight-per-day selection, direct nutrition/exercise aggregation, and UTC fallback. Session-lifecycle regression coverage verifies cleanup when request handling raises and repeated Dashboard/Analytics requests. PostgreSQL smoke tests use a disposable verification database.

Reminder tests cover CRUD, schedule validation, ownership, daily/weekly applicability, due/upcoming status, Profile timezone, UTC fallback, Dashboard integration, and request-session regression behavior.
