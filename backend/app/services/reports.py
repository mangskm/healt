from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.profile import WeightUnit
from app.models.user import User
from app.repositories.profile import ProfileRepository
from app.repositories.reports import ReportRepository
from app.schemas.reports import (
    MonthlyActivitySummary,
    MonthlyExerciseSummary,
    MonthlyNutritionSummary,
    MonthlyNutritionTotals,
    MonthlyReportPeriod,
    MonthlyReportResponse,
    MonthlyWeightSummary,
)
from app.services.reporting import month_range
from app.services.weight_units import from_kilograms


class ReportService:
    """Descriptive monthly summaries of records already entered by one user."""

    def __init__(self, db: Session, user: User) -> None:
        self._user = user
        self._profiles = ProfileRepository(db)
        self._reports = ReportRepository(db)

    def monthly(self, month: str | None, now: datetime | None = None) -> MonthlyReportResponse:
        profile = self._profiles.get_for_user(self._user.id)
        period = month_range(profile, month, now)
        weights = self._reports.weight_records_in_range(self._user.id, period.start_utc, period.end_utc)
        meals = self._reports.meals_in_range(self._user.id, period.start_utc, period.end_utc)
        exercise = self._reports.exercise_sessions_in_range(self._user.id, period.start_utc, period.end_utc)

        weight_unit = profile.weight_unit if profile and profile.weight_unit else WeightUnit.KILOGRAMS
        weight_values = [from_kilograms(Decimal(str(record.weight_kg)), weight_unit) for record in weights]
        all_items = [item for meal in meals for item in meal.items]
        nutrition_fields = ("calories_kcal", "protein_g", "carbohydrates_g", "fat_g")
        totals = {
            field: sum((Decimal(str(getattr(item, field))) for item in all_items if getattr(item, field) is not None), Decimal("0"))
            for field in nutrition_fields
        }
        items_with_any_nutrition = sum(any(getattr(item, field) is not None for field in nutrition_fields) for item in all_items)
        distance_sessions = [session for session in exercise if session.distance_km is not None]
        calorie_sessions = [session for session in exercise if session.calories_burned_kcal is not None]
        activity_totals: dict[str, tuple[int, int]] = {}
        for session in exercise:
            activity_type = session.activity_type.value
            count, duration = activity_totals.get(activity_type, (0, 0))
            activity_totals[activity_type] = (count + 1, duration + session.duration_minutes)

        return MonthlyReportResponse(
            period=MonthlyReportPeriod(
                month=period.start_date.strftime("%Y-%m"),
                timezone=period.timezone_name,
                start_date=period.start_date,
                end_date=period.end_date,
            ),
            weight=MonthlyWeightSummary(
                unit=weight_unit,
                measurement_count=len(weight_values),
                first=float(weight_values[0]) if weight_values else None,
                latest=float(weight_values[-1]) if weight_values else None,
                minimum=float(min(weight_values)) if weight_values else None,
                maximum=float(max(weight_values)) if weight_values else None,
                average=float(sum(weight_values) / len(weight_values)) if weight_values else None,
                recorded_change=float(weight_values[-1] - weight_values[0]) if len(weight_values) >= 2 else None,
            ),
            nutrition=MonthlyNutritionSummary(
                meal_count=len(meals),
                item_count=len(all_items),
                items_with_any_nutrition=items_with_any_nutrition,
                nutrition_missing_item_count=len(all_items) - items_with_any_nutrition,
                totals=MonthlyNutritionTotals(**{field: float(value) for field, value in totals.items()}),
            ),
            exercise=MonthlyExerciseSummary(
                distance_unit="km",
                session_count=len(exercise),
                total_duration_minutes=sum(session.duration_minutes for session in exercise),
                distance=float(sum((Decimal(str(session.distance_km)) for session in distance_sessions), Decimal("0"))),
                distance_session_count=len(distance_sessions),
                calories_burned_kcal=float(sum((Decimal(str(session.calories_burned_kcal)) for session in calorie_sessions), Decimal("0"))),
                calories_entered_session_count=len(calorie_sessions),
                activity_types=[
                    MonthlyActivitySummary(activity_type=activity_type, session_count=count, duration_minutes=duration)
                    for activity_type, (count, duration) in sorted(activity_totals.items())
                ],
            ),
        )
