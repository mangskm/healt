# Features

## Implemented in Phases 0–7

- Responsive foundational Today page
- Visible frontend-to-backend health connection status
- REST health endpoint with a database connectivity check
- PostgreSQL, migration, and test infrastructure
- Local user/profile foundation with basic optional information and unit preferences
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

## Not yet implemented

Water tracking, sleep tracking, habits, AI assistant, authentication, notifications, and Phase 8+ features are deliberately deferred to their assigned phases. Food databases, barcode scanning, food recognition, calorie targets, nutrition recommendations, dieting features, exercise recommendations, pace analysis, automatic calorie estimation, predictive trends, and recommendations are not implemented.
