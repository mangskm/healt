# API

The API uses the `/api/v1` version prefix. Interactive OpenAPI documentation is exposed by FastAPI at `/docs` during development.

## Health

`GET /api/v1/health`

Checks that the API can execute a database query.

Successful response (`200`):

```json
{
  "status": "ok",
  "database": "connected"
}
```

## Profile

`GET /api/v1/profile`

Returns the configured local profile. It returns `404` with `Profile not configured.` before the first update.

`PATCH /api/v1/profile`

Creates the local profile on first use or partially updates explicitly supplied fields. Sending `null` clears an optional value. Supported fields are `preferred_name`, `date_of_birth`, `sex`, `height_cm` (50–300), `weight_unit` (`kg` or `lb`), `height_unit` (`cm` or `ft_in`), and an IANA `timezone`.

This profile stores tracking preferences and basic information only; it does not calculate health targets or provide diagnosis.

## Weight records

All records belong to the current local user. The database stores canonical `weight_kg`; requests submit `weight` with an explicit `unit` (`kg` or `lb`). Responses expose `weight_kg` so the unit is never ambiguous.

- `GET /api/v1/weight-records?limit=50&offset=0` returns `{ items, total, latest }`, ordered by `recorded_at` descending. `limit` is 1–100.
- `POST /api/v1/weight-records` creates a record and returns `201`.
- `GET /api/v1/weight-records/{record_id}` returns a record owned by the local user.
- `PATCH /api/v1/weight-records/{record_id}` updates supplied fields. `weight` and `unit` must be supplied together.
- `DELETE /api/v1/weight-records/{record_id}` deletes the record and returns `204`.

The create payload requires an explicit unit, positive weight, timezone-aware `recorded_at` not in the future, and accepts an optional note up to 500 characters. A missing or non-owned record returns `404`.

## Goals

Only `target_weight` goals are available. Their stored canonical field is `target_value_kg`; create/update requests send a positive `target_value` plus explicit `kg` or `lb` unit.

- `GET /api/v1/goals?limit=50&offset=0`
- `POST /api/v1/goals` (`201`)
- `GET /api/v1/goals/{goal_id}`
- `PATCH /api/v1/goals/{goal_id}`
- `DELETE /api/v1/goals/{goal_id}` (`204`)

Statuses are manual: `active`, `completed`, or `cancelled`. Goals are scoped to the local user; missing or non-owned goals return `404`.

## Meals

Meals and Meal Items are manually entered tracking data for the current local user. The API uses separate item endpoints: create a Meal first, then add, edit, or remove its items. Meal responses include their items; list and detail reads load them efficiently.

- `GET /api/v1/meals?limit=50&offset=0` returns `{ items, total }` ordered by `eaten_at` descending. `limit` is 1–100.
- `POST /api/v1/meals` creates a Meal and returns `201`.
- `GET /api/v1/meals/{meal_id}` reads one owned Meal with its items.
- `PATCH /api/v1/meals/{meal_id}` updates supplied meal fields.
- `DELETE /api/v1/meals/{meal_id}` deletes the Meal and cascades to its items, returning `204`.
- `POST /api/v1/meals/{meal_id}/items` creates an item and returns `201`.
- `PATCH /api/v1/meals/{meal_id}/items/{item_id}` updates supplied item fields.
- `DELETE /api/v1/meals/{meal_id}/items/{item_id}` deletes an item and returns `204`.

`meal_type` is one of `breakfast`, `lunch`, `dinner`, `snack`, or `other`. `eaten_at` must include a timezone and cannot be in the future. An item requires a nonblank food name, positive quantity, and `g`, `ml`, `serving`, or `piece` unit. Optional calories and macronutrient values are per-entered-quantity tracking values and must be non-negative. No targets, recommendations, or automatic nutrition calculations are exposed.

## Exercise sessions

- `GET /api/v1/exercise-sessions?limit=50&offset=0` returns `{ items, total }` newest first; limit is 1–100.
- `POST /api/v1/exercise-sessions` creates a session (`201`).
- `GET`, `PATCH`, and `DELETE /api/v1/exercise-sessions/{session_id}` read, update, or delete an owned session (`204` for deletion).

Activity types are `walking`, `running`, `cycling`, `strength_training`, `swimming`, `sports`, and `other`. `performed_at` needs a timezone and cannot be future; duration is a positive integer in minutes. Optional distance must include a positive `distance` and `distance_unit` of `km` or `mi`; responses expose unambiguous canonical `distance_km`. Optional `calories_burned_kcal` is manually entered and non-negative. No calorie estimation, recommendation, or exercise analytics is provided.

## Dashboard

`GET /api/v1/dashboard` is read-only. It returns profile summary, latest weight, active goals, and current-day meal/exercise totals. “Today” uses the Profile IANA timezone, or UTC when no timezone is configured. Nutrition sums known entered values and reports missing-item counts; it provides no targets, net calories, trends, scoring, or recommendations.

## Analytics

`GET /api/v1/analytics?period=7d|30d` returns read-only descriptive history. Periods mean 7 or 30 local calendar dates including today, using Profile timezone or UTC fallback. Weight series selects the latest record per local date and never fabricates missing dates. Meal and Exercise daily series include zero days; nutrition sums direct entered values, counts an item as missing only when every nutrition field is absent, and never imputes values. Exercise totals duration, canonical kilometers, manually entered calories, and activity types. No analytics table or migration exists.
