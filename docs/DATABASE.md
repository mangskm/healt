# Database

## Phase 1 schema

PostgreSQL 16 is provisioned by Docker Compose. SQLAlchemy connects through the `DATABASE_URL` environment variable, and Alembic is configured in `database/migrations`.

Migration `0001_profile_foundation` creates:

- `users`: a UUID primary key and audit timestamps. Until authentication is introduced, the first profile update creates the single local owner row.
- `user_profiles`: a one-to-one record linked to `users` by a unique, indexed foreign key. It stores optional display name, date of birth, sex, height in centimeters, unit preferences, timezone, and audit timestamps.

The database enforces the 50–300 cm height range and valid unit/sex values. The API additionally validates future dates and IANA timezones.

## Phase 2 schema

Migration `0002_weight_records` creates `weight_records` with UUID primary key, `user_id` foreign key, `weight_kg`, `recorded_at`, optional note, and audit timestamps. A composite index on `(user_id, recorded_at)` supports each user's reverse-chronological history; a database constraint requires a positive canonical weight.

`weight_kg` is the only stored measurement unit. It is `NUMERIC(10,3)` to avoid floating-point drift and preserve measurements to 0.001 kg. API clients must send a positive `weight` with an explicit `kg` or `lb` unit; the backend converts pounds using the exact factor `0.45359237` and rounds only the stored canonical value to three decimals. The UI displays and pre-fills converted values to two decimals. The numeric precision is a technical storage bound, not a health recommendation.

No calorie targets, diagnoses, charts, or analytics are stored in this phase.

## Phase 3 schema

Migration `0003_goals` adds `goals`, owned by `users`, with `goal_type`, canonical `target_value_kg`, optional `target_date`, manual `status`, and timestamps. It has positive-value, foreign-key, enum, and `(user_id, status)` index constraints. Only `target_weight` is currently supported. Its canonical value and kg/lb conversion follow the Weight Record convention exactly; completion is manual and never inferred from measurements.

## Phase 4 schema

Migration `0004_food_tracking` adds `meals` and `meal_items`.

- `meals` belongs to `users` and stores a `meal_type` (`breakfast`, `lunch`, `dinner`, `snack`, or `other`), timezone-aware `eaten_at`, optional 500-character note, and audit timestamps. `(user_id, eaten_at)` is indexed for reverse-chronological history.
- `meal_items` belongs to `meals` and stores required `food_name` (up to 200 characters), positive `quantity`, supported entered unit (`g`, `ml`, `serving`, or `piece`), optional `calories_kcal`, `protein_g`, `carbohydrates_g`, and `fat_g`, plus audit timestamps. All numeric tracking values use `NUMERIC(10,3)`; nutrition values are nullable but never negative.
- Deleting a Meal cascades to its Meal Items at the database foreign-key level (`meal_items.meal_id ON DELETE CASCADE`). Deleting a User cascades to its Meals, and consequently their items. This behavior is intentional so no orphaned food rows remain.

Meal type and quantity-unit SQLAlchemy enums persist their lowercase `.value` strings. This matches the migration check constraints and API values.

## Phase 5 schema

Migration `0005_exercise_tracking` adds `exercise_sessions`, owned by `users`. It stores lowercase `activity_type`, timezone-aware `performed_at`, positive integer `duration_minutes`, optional canonical `distance_km`, optional manually entered `calories_burned_kcal`, optional 500-character note, and timestamps. `(user_id, performed_at)` supports reverse-chronological history. Distance and calories use `NUMERIC(10,3)` with positive/non-negative checks. `activity_type` enum values persist their `.value` strings, matching the API and migration constraints.

Distance is stored in canonical kilometers. API input accepts `km` or `mi`; miles are multiplied by exact `1.609344` and the stored kilometer value is rounded half-up to 0.001 km.

## Migration workflow

## Phase 6 dashboard

Phase 6 adds no tables or migration. Dashboard reads existing user-scoped records; Alembic remains at `0005_exercise_tracking`.

Its timezone-aware day boundaries are query-time calculations only; stored timestamps are not rewritten.

## Phase 7 analytics

Phase 7 creates no table or migration; Alembic remains `0005_exercise_tracking`. Weight chart series use the latest measurement per local day without fabricating missing days. Nutrition and Exercise are direct entered-data aggregates. An item is marked missing only when all nutrition fields are absent; partial entered values are summed and never imputed. Exercise distance remains canonical kilometers and calories remain manually entered.

## Phase 8 reminders

Migration `0006_notifications` adds `reminders`, owned by `users`. It stores lowercase `reminder_type` (`weight`, `meal`, `exercise`, `custom`), a required trimmed title, local wall-clock `reminder_time` (`TIME`), lowercase `schedule_type` (`daily`, `weekly`), optional weekday, enabled state, optional note, and timestamps. A database check enforces daily schedules have no weekday and weekly schedules have weekday `0` (Monday) through `6` (Sunday). The migration is reversible. It does not store notification occurrences, delivery history, or external notification state.

From `backend/`, after setting `DATABASE_URL`:

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

Review autogenerated revisions before applying them. Migrations must include appropriate primary keys, foreign keys, timestamps, constraints, and indexes for the domain being added.
