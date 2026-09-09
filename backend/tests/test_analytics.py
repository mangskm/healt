from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.models.exercise import ActivityType, ExerciseSession
from app.models.meal import FoodUnit, Meal, MealItem, MealType
from app.models.profile import UserProfile
from app.models.user import User
from app.models.weight import WeightRecord
from app.services.analytics import AnalyticsService


def test_empty_analytics_and_invalid_period(client: TestClient) -> None:
    empty = client.get("/api/v1/analytics?period=7d")
    invalid = client.get("/api/v1/analytics?period=90d")
    assert empty.status_code == 200
    assert empty.json()["timezone"] == "UTC"
    assert len(empty.json()["nutrition"]["daily"]) == 7
    assert invalid.status_code == 422


def test_analytics_groups_profile_local_dates_and_describes_data(db_session) -> None:
    user = User(); db_session.add(user); db_session.flush()
    db_session.add(UserProfile(user_id=user.id, timezone="Asia/Bangkok"))
    db_session.add_all([
        WeightRecord(user_id=user.id, weight_kg=70, recorded_at=datetime(2026, 9, 5, 18, tzinfo=timezone.utc)),
        WeightRecord(user_id=user.id, weight_kg=69, recorded_at=datetime(2026, 9, 5, 20, tzinfo=timezone.utc)),
    ])
    meal = Meal(user_id=user.id, meal_type=MealType.BREAKFAST, eaten_at=datetime(2026, 9, 5, 18, tzinfo=timezone.utc)); db_session.add(meal); db_session.flush()
    db_session.add_all([MealItem(meal_id=meal.id, food_name="Known", quantity=1, unit=FoodUnit.PIECE, calories_kcal=100, protein_g=2), MealItem(meal_id=meal.id, food_name="Missing", quantity=1, unit=FoodUnit.PIECE)])
    db_session.add(ExerciseSession(user_id=user.id, activity_type=ActivityType.WALKING, performed_at=datetime(2026, 9, 5, 18, tzinfo=timezone.utc), duration_minutes=30, distance_km=2))
    db_session.commit()
    result = AnalyticsService(db_session, user).get("7d", now=datetime(2026, 9, 6, 12, tzinfo=timezone.utc))
    assert result.start_date.isoformat() == "2026-08-31" and result.end_date.isoformat() == "2026-09-06"
    assert result.weight["measurement_count"] == 2 and result.weight["series"][0]["weight_kg"] == 69
    assert result.nutrition["totals"]["calories_kcal"] == 100 and result.nutrition["nutrition_missing_item_count"] == 1
    assert result.exercise["activity_types"]["walking"]["duration_minutes"] == 30
