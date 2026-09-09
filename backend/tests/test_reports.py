import csv
from datetime import datetime, timezone
from io import StringIO

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.models.exercise import ActivityType, ExerciseSession
from app.models.meal import FoodUnit, Meal, MealItem, MealType
from app.models.profile import UserProfile, WeightUnit
from app.models.user import User
from app.models.weight import WeightRecord
from app.services.reports import ReportService
from app.services.reporting import month_range


def test_monthly_report_requires_authentication(anonymous_client: TestClient) -> None:
    assert anonymous_client.get("/api/v1/reports/monthly?month=2026-09").status_code == 401
    assert anonymous_client.get("/api/v1/exports/weight.csv?month=2026-09").status_code == 401


def test_monthly_report_uses_profile_timezone_and_direct_entered_values(db_session) -> None:
    user = User()
    db_session.add(user)
    db_session.flush()
    db_session.add(UserProfile(user_id=user.id, timezone="Asia/Bangkok", weight_unit=WeightUnit.POUNDS))
    db_session.add_all([
        WeightRecord(user_id=user.id, weight_kg=70, recorded_at=datetime(2026, 8, 31, 17, tzinfo=timezone.utc)),
        WeightRecord(user_id=user.id, weight_kg=69, recorded_at=datetime(2026, 9, 15, 1, tzinfo=timezone.utc)),
        WeightRecord(user_id=user.id, weight_kg=68, recorded_at=datetime(2026, 9, 30, 17, tzinfo=timezone.utc)),
    ])
    meal = Meal(user_id=user.id, meal_type=MealType.BREAKFAST, eaten_at=datetime(2026, 8, 31, 17, tzinfo=timezone.utc))
    outside_meal = Meal(user_id=user.id, meal_type=MealType.DINNER, eaten_at=datetime(2026, 9, 30, 17, tzinfo=timezone.utc))
    db_session.add_all([meal, outside_meal])
    db_session.flush()
    db_session.add_all([
        MealItem(meal_id=meal.id, food_name="Rice", quantity=1, unit=FoodUnit.SERVING, calories_kcal=200, protein_g=4),
        MealItem(meal_id=meal.id, food_name="Unknown", quantity=1, unit=FoodUnit.PIECE),
    ])
    db_session.add_all([
        ExerciseSession(user_id=user.id, activity_type=ActivityType.WALKING, performed_at=datetime(2026, 9, 1, 3, tzinfo=timezone.utc), duration_minutes=30, distance_km=2, calories_burned_kcal=100),
        ExerciseSession(user_id=user.id, activity_type=ActivityType.RUNNING, performed_at=datetime(2026, 9, 30, 17, tzinfo=timezone.utc), duration_minutes=50, distance_km=8, calories_burned_kcal=500),
    ])
    db_session.commit()

    report = ReportService(db_session, user).monthly("2026-09")

    assert report.period.timezone == "Asia/Bangkok"
    assert report.period.start_date.isoformat() == "2026-09-01"
    assert report.period.end_date.isoformat() == "2026-09-30"
    assert report.weight.unit is WeightUnit.POUNDS
    assert report.weight.measurement_count == 2
    assert report.weight.first == 154.324
    assert report.weight.latest == 152.119
    assert report.weight.recorded_change == -2.205
    assert report.nutrition.meal_count == 1
    assert report.nutrition.item_count == 2
    assert report.nutrition.totals.calories_kcal == 200
    assert report.nutrition.nutrition_missing_item_count == 1
    assert report.exercise.session_count == 1
    assert report.exercise.total_duration_minutes == 30
    assert report.exercise.distance == 2
    assert report.exercise.calories_burned_kcal == 100
    assert report.exercise.activity_types[0].activity_type == "walking"


def test_monthly_report_empty_and_single_weight_have_no_fabricated_change(client: TestClient, db_session) -> None:
    user = db_session.scalar(select(User).where(User.email == "test@example.com"))
    assert user is not None
    db_session.add(WeightRecord(user_id=user.id, weight_kg=70, recorded_at=datetime(2026, 9, 1, tzinfo=timezone.utc)))
    db_session.commit()

    response = client.get("/api/v1/reports/monthly?month=2026-09")

    assert response.status_code == 200
    body = response.json()
    assert body["period"]["timezone"] == "UTC"
    assert body["weight"]["measurement_count"] == 1
    assert body["weight"]["recorded_change"] is None
    assert body["nutrition"]["meal_count"] == 0
    assert body["exercise"]["session_count"] == 0
    assert client.get("/api/v1/reports/monthly?month=2026-9").status_code == 422


def test_profile_api_timezone_flows_to_monthly_report(client: TestClient) -> None:
    profile = client.patch("/api/v1/profile", json={"timezone": "Asia/Bangkok"})
    report = client.get("/api/v1/reports/monthly?month=2026-09")

    assert profile.status_code == 200
    assert profile.json()["timezone"] == "Asia/Bangkok"
    assert report.status_code == 200
    assert report.json()["period"]["timezone"] == "Asia/Bangkok"


def test_missing_or_invalid_profile_timezone_falls_back_to_utc(db_session) -> None:
    user = User()
    db_session.add(user)
    db_session.flush()
    db_session.add(UserProfile(user_id=user.id, timezone="not-a-real-timezone"))
    db_session.commit()

    report = ReportService(db_session, user).monthly("2026-09")

    assert report.period.timezone == "UTC"


def test_asia_bangkok_month_boundaries_use_a_half_open_utc_range(db_session) -> None:
    user = User()
    db_session.add(user)
    db_session.flush()
    profile = UserProfile(user_id=user.id, timezone="Asia/Bangkok")
    db_session.add(profile)
    db_session.commit()

    period = month_range(profile, "2026-09")

    assert period.start_utc == datetime(2026, 8, 31, 17, tzinfo=timezone.utc)
    assert period.end_utc == datetime(2026, 9, 30, 17, tzinfo=timezone.utc)


def test_monthly_report_and_csv_never_include_another_users_records(client: TestClient, db_session) -> None:
    other_user = User(email="other@example.com", password_hash="unused")
    db_session.add(other_user)
    db_session.flush()
    db_session.add(WeightRecord(user_id=other_user.id, weight_kg=99, recorded_at=datetime(2026, 9, 1, tzinfo=timezone.utc), note="private"))
    meal = Meal(user_id=other_user.id, meal_type=MealType.LUNCH, eaten_at=datetime(2026, 9, 1, tzinfo=timezone.utc))
    db_session.add(meal)
    db_session.flush()
    db_session.add(MealItem(meal_id=meal.id, food_name="Private food", quantity=1, unit=FoodUnit.SERVING, calories_kcal=999))
    db_session.add(ExerciseSession(user_id=other_user.id, activity_type=ActivityType.RUNNING, performed_at=datetime(2026, 9, 1, tzinfo=timezone.utc), duration_minutes=99, distance_km=9))
    db_session.commit()

    report = client.get("/api/v1/reports/monthly?month=2026-09")
    export = client.get("/api/v1/exports/weight.csv?range=month&month=2026-09")

    assert report.status_code == 200
    assert report.json()["weight"]["measurement_count"] == 0
    assert report.json()["nutrition"]["meal_count"] == 0
    assert report.json()["exercise"]["session_count"] == 0
    assert export.status_code == 200
    assert "99" not in export.content.decode("utf-8-sig")
    assert "private" not in export.content.decode("utf-8-sig")


def test_csv_exports_are_utf8_timezone_aware_and_spreadsheet_safe(client: TestClient, db_session) -> None:
    user = db_session.scalar(select(User).where(User.email == "test@example.com"))
    assert user is not None
    db_session.add(UserProfile(user_id=user.id, timezone="Asia/Bangkok", weight_unit=WeightUnit.POUNDS))
    db_session.add(WeightRecord(user_id=user.id, weight_kg=70, recorded_at=datetime(2026, 8, 31, 17, tzinfo=timezone.utc), note="=SUM(A1)"))
    meal = Meal(user_id=user.id, meal_type=MealType.LUNCH, eaten_at=datetime(2026, 8, 31, 17, tzinfo=timezone.utc), note="-meal note")
    db_session.add(meal)
    db_session.flush()
    db_session.add(MealItem(meal_id=meal.id, food_name="อาหารไทย", quantity=1, unit=FoodUnit.SERVING, protein_g=3))
    db_session.add(ExerciseSession(user_id=user.id, activity_type=ActivityType.WALKING, performed_at=datetime(2026, 8, 31, 17, tzinfo=timezone.utc), duration_minutes=20, distance_km=1.5, note="@note"))
    db_session.commit()

    weight = client.get("/api/v1/exports/weight.csv?range=month&month=2026-09")
    meals = client.get("/api/v1/exports/meals.csv?range=custom&start=2026-09-01&end=2026-09-01")
    exercise = client.get("/api/v1/exports/exercise.csv?range=last_30_days")

    assert weight.status_code == meals.status_code == exercise.status_code == 200
    assert weight.headers["content-type"] == "text/csv; charset=utf-8"
    assert 'attachment; filename="weight-2026-09-01-to-2026-09-30.csv"' == weight.headers["content-disposition"]
    weight_csv = weight.content.decode("utf-8-sig")
    meals_csv = meals.content.decode("utf-8-sig")
    exercise_csv = exercise.content.decode("utf-8-sig")
    assert weight.content.startswith(b"\xef\xbb\xbf")
    assert "2026-09-01T00:00:00+07:00" in weight_csv
    assert "'='" not in weight_csv
    assert "'=SUM(A1)" in weight_csv
    assert "อาหารไทย" in meals_csv
    assert "'-meal note" in meals_csv
    meal_row = next(csv.DictReader(StringIO(meals_csv)))
    assert meal_row["calories_kcal"] == ""
    assert meal_row["protein_g"] == "3"
    assert meal_row["carbohydrates_g"] == ""
    assert meal_row["fat_g"] == ""
    assert "'@note" in exercise_csv


def test_csv_range_validation_and_empty_export_headers(client: TestClient) -> None:
    invalid = client.get("/api/v1/exports/weight.csv?range=custom&start=2026-09-02&end=2026-09-01")
    missing = client.get("/api/v1/exports/weight.csv?range=custom")
    empty = client.get("/api/v1/exports/exercise.csv?range=month&month=2026-09")

    assert invalid.status_code == 422
    assert missing.status_code == 422
    assert empty.status_code == 200
    assert empty.content.decode("utf-8-sig") == "performed_at_local,activity_type,duration_minutes,distance,distance_unit,calories_entered_kcal,note\n"
