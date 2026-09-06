from datetime import datetime, time, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.goal import Goal, GoalStatus
from app.models.meal import Meal
from app.models.exercise import ExerciseSession
from app.repositories.profile import ProfileRepository
from app.repositories.user import UserRepository
from app.repositories.weight import WeightRecordRepository
from app.schemas.dashboard import DashboardExercise, DashboardExerciseSummary, DashboardGoal, DashboardMeal, DashboardMealSummary, DashboardProfile, DashboardResponse, DashboardWeight


class DashboardService:
    """Read-only composition of the user's existing tracking records."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._users = UserRepository(db)
        self._profiles = ProfileRepository(db)
        self._weights = WeightRecordRepository(db)

    def get_dashboard(self, now: datetime | None = None) -> DashboardResponse:
        user = self._users.get_or_create_local_user()
        profile = self._profiles.get_profile()
        timezone_name = profile.timezone if profile and profile.timezone else "UTC"
        local_zone = ZoneInfo(timezone_name)
        current = now or datetime.now(timezone.utc)
        local_day = current.astimezone(local_zone).date()
        start = datetime.combine(local_day, time.min, tzinfo=local_zone).astimezone(timezone.utc)
        end = datetime.combine(local_day.fromordinal(local_day.toordinal() + 1), time.min, tzinfo=local_zone).astimezone(timezone.utc)
        latest = self._weights.latest_for_user(user.id)
        goals = list(self._db.scalars(select(Goal).where(Goal.user_id == user.id, Goal.status == GoalStatus.ACTIVE).order_by(Goal.created_at.desc())))
        meals = list(self._db.scalars(select(Meal).options(selectinload(Meal.items)).where(Meal.user_id == user.id, Meal.eaten_at >= start, Meal.eaten_at < end).order_by(Meal.eaten_at.desc())))
        sessions = list(self._db.scalars(select(ExerciseSession).where(ExerciseSession.user_id == user.id, ExerciseSession.performed_at >= start, ExerciseSession.performed_at < end).order_by(ExerciseSession.performed_at.desc())))
        meal_items = [item for meal in meals for item in meal.items]
        known = lambda field: sum((Decimal(str(getattr(item, field))) for item in meal_items if getattr(item, field) is not None), Decimal("0"))
        nutrition_complete = sum(all(getattr(item, field) is not None for field in ("calories_kcal", "protein_g", "carbohydrates_g", "fat_g")) for item in meal_items)
        distance_sessions = [session for session in sessions if session.distance_km is not None]
        calorie_sessions = [session for session in sessions if session.calories_burned_kcal is not None]
        return DashboardResponse(
            timezone=timezone_name, date=local_day,
            profile=DashboardProfile(preferred_name=profile.preferred_name, weight_unit=profile.weight_unit.value if profile.weight_unit else None) if profile else None,
            latest_weight=DashboardWeight(id=latest.id, weight_kg=latest.weight_kg, recorded_at=latest.recorded_at) if latest else None,
            active_goals=[DashboardGoal(id=goal.id, target_value_kg=goal.target_value_kg, target_date=goal.target_date, status=goal.status.value) for goal in goals],
            meals=DashboardMealSummary(count=len(meals), items=[DashboardMeal(id=meal.id, meal_type=meal.meal_type.value, eaten_at=meal.eaten_at, item_count=len(meal.items)) for meal in meals], item_count=len(meal_items), nutrition_item_count=nutrition_complete, nutrition_missing_item_count=len(meal_items)-nutrition_complete, calories_kcal=float(known("calories_kcal")), protein_g=float(known("protein_g")), carbohydrates_g=float(known("carbohydrates_g")), fat_g=float(known("fat_g"))),
            exercise=DashboardExerciseSummary(count=len(sessions), items=[DashboardExercise(id=session.id, activity_type=session.activity_type.value, performed_at=session.performed_at, duration_minutes=session.duration_minutes, distance_km=session.distance_km, calories_burned_kcal=session.calories_burned_kcal) for session in sessions], duration_minutes=sum(session.duration_minutes for session in sessions), distance_km=float(sum((Decimal(str(session.distance_km)) for session in distance_sessions), Decimal("0"))), distance_session_count=len(distance_sessions), calories_burned_kcal=float(sum((Decimal(str(session.calories_burned_kcal)) for session in calorie_sessions), Decimal("0"))), calories_entered_session_count=len(calorie_sessions)),
        )
