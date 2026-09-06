from datetime import datetime, time, timezone

from app.models.exercise import ActivityType, ExerciseSession
from app.models.goal import Goal, GoalStatus, GoalType
from app.models.meal import FoodUnit, Meal, MealItem, MealType
from app.models.profile import UserProfile, WeightUnit
from app.models.weight import WeightRecord
from app.models.user import User
from app.models.reminder import Reminder, ReminderScheduleType, ReminderType
from app.services.dashboard import DashboardService


def test_dashboard_empty_and_profile_timezone(client) -> None:
    response = client.get("/api/v1/dashboard")
    assert response.status_code == 200
    assert response.json()["timezone"] == "UTC"
    assert response.json()["meals"]["count"] == 0


def test_dashboard_aggregates_current_local_day_and_excludes_boundaries(db_session) -> None:
    user = User(); db_session.add(user); db_session.flush()
    profile = UserProfile(user_id=user.id, timezone="Asia/Bangkok", weight_unit=WeightUnit.KILOGRAMS); db_session.add(profile)
    db_session.add(WeightRecord(user_id=user.id, weight_kg=70, recorded_at=datetime(2026, 9, 6, 1, tzinfo=timezone.utc)))
    db_session.add(Goal(user_id=user.id, goal_type=GoalType.TARGET_WEIGHT, target_value_kg=65, status=GoalStatus.ACTIVE))
    inside = Meal(user_id=user.id, meal_type=MealType.LUNCH, eaten_at=datetime(2026, 9, 6, 2, tzinfo=timezone.utc)); outside = Meal(user_id=user.id, meal_type=MealType.DINNER, eaten_at=datetime(2026, 9, 6, 18, tzinfo=timezone.utc)); db_session.add_all([inside, outside]); db_session.flush()
    db_session.add(MealItem(meal_id=inside.id, food_name="Rice", quantity=1, unit=FoodUnit.SERVING, calories_kcal=200, protein_g=4)); db_session.add(MealItem(meal_id=inside.id, food_name="Fruit", quantity=1, unit=FoodUnit.PIECE))
    db_session.add(ExerciseSession(user_id=user.id, activity_type=ActivityType.WALKING, performed_at=datetime(2026, 9, 6, 3, tzinfo=timezone.utc), duration_minutes=30, distance_km=2, calories_burned_kcal=100)); db_session.commit()
    db_session.add(Reminder(user_id=user.id, reminder_type=ReminderType.WEIGHT, title="Log weight", reminder_time=time(8), schedule_type=ReminderScheduleType.DAILY)); db_session.commit()
    dashboard = DashboardService(db_session).get_dashboard(now=datetime(2026, 9, 6, 12, tzinfo=timezone.utc))
    assert dashboard.timezone == "Asia/Bangkok" and dashboard.meals.count == 1
    assert dashboard.meals.calories_kcal == 200 and dashboard.meals.nutrition_missing_item_count == 2
    assert dashboard.exercise.duration_minutes == 30 and dashboard.exercise.distance_km == 2
    assert dashboard.reminders[0].title == "Log weight"
