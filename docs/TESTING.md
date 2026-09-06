# Testing

## Backend

Backend tests use Pytest and FastAPI's `TestClient`. The test database substitutes in-memory SQLite, so it verifies health, Profile, Weight Record, Goal, Meal, and Meal Item CRUD, validation, ordering, pagination, ownership filtering, cascade behavior, and conversion logic.

```bash
cd backend
pytest
```

Database-specific migrations and PostgreSQL behavior are verified through the Compose stack. Phase 4 applies `0004_food_tracking` through `PostgresqlImpl`, checks the Alembic head and health endpoint, then runs a synthetic Meal/Meal Item CRUD smoke test and cleans up its test data.

## Frontend

Frontend component tests use Vitest, jsdom, and Testing Library.

```bash
cd frontend
npm test
npm run build
```

Frontend tests cover the health indicator, Profile save flow, Weight behavior, Goals empty/create/validation behavior, Meals empty/history/create-with-multiple-items/delete/edit behavior, meal-total utility, and kg/lb conversion utility.
