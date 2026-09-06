from datetime import date
from pydantic import BaseModel

class WeightPoint(BaseModel): date: date; weight_kg: float
class NutritionPoint(BaseModel): date: date; meal_count: int; calories_kcal: float; protein_g: float; carbohydrates_g: float; fat_g: float
class ExercisePoint(BaseModel): date: date; session_count: int; duration_minutes: int; distance_km: float; calories_burned_kcal: float
class AnalyticsResponse(BaseModel):
    period: str; timezone: str; start_date: date; end_date: date
    weight: dict; nutrition: dict; exercise: dict
