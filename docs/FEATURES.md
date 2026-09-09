# Features

## Implemented in Phases 0–9

- Responsive foundational Today page
- Visible frontend-to-backend health connection status
- REST health endpoint with a database connectivity check
- PostgreSQL, migration, and test infrastructure
- Authenticated user/profile foundation with basic optional information and unit preferences
- Profile read/update API and Profile page
- Weight Record CRUD API with local-user ownership filtering and pagination
- Weight page with latest measurement, history, add/edit/delete flows, empty/loading/saving/error states
- Canonical kilogram storage with kg/lb input and display conversion
- Target-weight Goal CRUD with manual active/completed/cancelled status
- Goals page with optional target date and informational latest-weight display
- Meal and Meal Item CRUD API with local-user ownership, pagination, validation, and intentional deletion cascade
- Meals page with manual multiple-item entry, edit/delete flows, optional per-meal direct nutrition totals, and loading/empty/saving/error states
- Exercise Session CRUD with local-user ownership, canonical km distance storage, manual optional calories, and pagination
- Exercise page with activity, timestamp, duration, km/mi input, optional manual calories, edit/delete, and loading/empty/saving/error states
- Read-only Dashboard with Profile-timezone daily Meal and Exercise summaries, latest weight, and active goals
- Read-only 7d/30d Analytics page for descriptive Weight, entered Nutrition, and Exercise history

- User-managed daily/weekly in-app reminders with Profile-timezone evaluation, due/upcoming state, CRUD management, and Today dashboard display
- Password sign-in with Argon2 hashes, server-side revocable sessions, protected routes, and a local-only account bootstrap command
- Production-like nginx frontend image, same-origin API proxy, dedicated Alembic migration service, and liveness/readiness checks
- Isolated Docker/PostgreSQL end-to-end verification of fresh migrations, authenticated ownership, direct SPA routing, backup/restore, and synthetic-data cleanup
- Post-Roadmap Iteration 1 responsive redesign: shared desktop/mobile navigation, polished Today dashboard, consistent cards/forms/states, confirmation dialogs, and lightweight success feedback
- Post-Roadmap Iteration 2 Reports: authenticated Profile-timezone monthly summaries for Weight, direct entered Nutrition, and manual Exercise records; responsive Reports route; and server-generated, UTF-8 CSV exports for Weight, Meal Items, and Exercise with spreadsheet formula-injection protection

## Not yet implemented

Water tracking, sleep tracking, habits, AI assistant, external notification delivery, report snapshots, export history, persisted generated files, charts, medical interpretation, recommendations, and health judgments remain deferred to separately approved work. Push, email, SMS, background notification workers, food databases, barcode scanning, food recognition, calorie targets, nutrition recommendations, dieting features, exercise recommendations, pace analysis, automatic calorie estimation, predictive trends, and recommendations are not implemented.
