# Testing

## Backend

Backend tests use Pytest and FastAPI's `TestClient`. The test database substitutes in-memory SQLite, so it verifies health, Profile, Weight Record, Goal, Meal, Meal Item, Exercise Session, and Dashboard aggregation behavior, including UTC fallback and Profile-timezone day boundaries.

```bash
cd backend
pytest
```

Database-specific migrations and PostgreSQL behavior are verified through the Compose stack. Phase 8 applies `0006_notifications`, checks the Alembic head and health endpoint, then runs a synthetic reminder CRUD/today-notification smoke test and cleans up its test data. Phase 9 verifies a fresh isolated PostgreSQL volume through `0007_authentication`, then exercises health/readiness, login/logout, authenticated Profile/Weight/Goal/Meal/Exercise/Reminder flows, user isolation, nginx proxying, and synthetic-data cleanup.

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

Phase 9 adds liveness/readiness, credentialed-CORS wildcard rejection, production cookie defaults, safe unexpected-error response coverage, and Docker build/configuration checks. Phase 9C completed an isolated running Compose smoke test: fresh migration chain, same-origin nginx routes including direct SPA paths, opaque-cookie login/logout, cross-user `404` isolation, and a custom-format PostgreSQL backup restored into a separate disposable database. Its frontend healthcheck also verifies nginx over `127.0.0.1` to avoid an Alpine `localhost` IPv6 mismatch.

Post-Roadmap Iteration 1 frontend tests retain the existing feature/auth coverage and add reusable confirmation-dialog behavior. Run `npm test` and `npm run build` from `frontend/`; the Docker frontend build continues to verify the nginx production artifact and relative same-origin API path.
