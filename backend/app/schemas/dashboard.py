from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class DashboardProfile(BaseModel):
    preferred_name: str | None
    weight_unit: str | None


class DashboardWeight(BaseModel):
    id: UUID
    weight_kg: float
    recorded_at: datetime


class DashboardGoal(BaseModel):
    id: UUID
    target_value_kg: float
    target_date: date | None
    status: str


class DashboardMeal(BaseModel):
    id: UUID
    meal_type: str
    eaten_at: datetime
    item_count: int


class DashboardMealSummary(BaseModel):
    count: int
    items: list[DashboardMeal]
    item_count: int
    nutrition_item_count: int
    nutrition_missing_item_count: int
    calories_kcal: float
    protein_g: float
    carbohydrates_g: float
    fat_g: float


class DashboardExercise(BaseModel):
    id: UUID
    activity_type: str
    performed_at: datetime
    duration_minutes: int
    distance_km: float | None
    calories_burned_kcal: float | None


class DashboardExerciseSummary(BaseModel):
    count: int
    items: list[DashboardExercise]
    duration_minutes: int
    distance_km: float
    distance_session_count: int
    calories_burned_kcal: float
    calories_entered_session_count: int


class DashboardResponse(BaseModel):
    timezone: str
    date: date
    profile: DashboardProfile | None
    latest_weight: DashboardWeight | None
    active_goals: list[DashboardGoal]
    meals: DashboardMealSummary
    exercise: DashboardExerciseSummary
