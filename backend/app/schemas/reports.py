from datetime import date

from pydantic import BaseModel

from app.models.profile import WeightUnit


class MonthlyReportPeriod(BaseModel):
    month: str
    timezone: str
    start_date: date
    end_date: date


class MonthlyWeightSummary(BaseModel):
    unit: WeightUnit
    measurement_count: int
    first: float | None
    latest: float | None
    minimum: float | None
    maximum: float | None
    average: float | None
    recorded_change: float | None


class MonthlyNutritionTotals(BaseModel):
    calories_kcal: float
    protein_g: float
    carbohydrates_g: float
    fat_g: float


class MonthlyNutritionSummary(BaseModel):
    meal_count: int
    item_count: int
    items_with_any_nutrition: int
    nutrition_missing_item_count: int
    totals: MonthlyNutritionTotals


class MonthlyActivitySummary(BaseModel):
    activity_type: str
    session_count: int
    duration_minutes: int


class MonthlyExerciseSummary(BaseModel):
    distance_unit: str
    session_count: int
    total_duration_minutes: int
    distance: float
    distance_session_count: int
    calories_burned_kcal: float
    calories_entered_session_count: int
    activity_types: list[MonthlyActivitySummary]


class MonthlyReportResponse(BaseModel):
    period: MonthlyReportPeriod
    weight: MonthlyWeightSummary
    nutrition: MonthlyNutritionSummary
    exercise: MonthlyExerciseSummary
