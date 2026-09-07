# Testing

## Backend

Backend tests use Pytest and FastAPI's `TestClient`. The test database substitutes in-memory SQLite, so it verifies health, Profile, Weight Record, Goal, Meal, Meal Item, Exercise Session, and Dashboard aggregation behavior, including UTC fallback and Profile-timezone day boundaries.

```bash
cd backend
pytest
```

Database-specific migrations and PostgreSQL behavior are verified through the Compose stack. Phase 8 applies `0006_notifications`, checks the Alembic head and health endpoint, then runs a synthetic reminder CRUD/today-notification smoke test and cleans up its test data. Phase 9A's local suite verifies `0007_authentication` metadata and migration head; PostgreSQL/Docker migration verification remains a later Phase 9 checkpoint.

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

Authentication tests cover anonymous `401` handling across protected endpoints, generic invalid credentials, HttpOnly login cookie behavior, token/password non-plaintext storage, `/auth/me`, revocation on logout, expiry, legacy bootstrap safety, and cross-user ownership isolation. Frontend tests cover sign-in, protected-route redirection, logout, and centralized expired-session recovery.

Phase 9B adds liveness/readiness, credentialed-CORS wildcard rejection, production cookie defaults, and safe unexpected-error response coverage. The Docker build verification builds backend/migrate and multi-stage nginx frontend images and validates Compose configuration; Phase 9C remains responsible for the isolated, running PostgreSQL/Docker smoke test.
