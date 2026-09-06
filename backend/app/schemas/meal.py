from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.meal import FoodUnit, MealType


class MealBase(BaseModel):
    meal_type: MealType
    eaten_at: datetime
    note: str | None = Field(default=None, max_length=500)

    @field_validator("eaten_at")
    @classmethod
    def validate_eaten_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Eaten timestamp must include a timezone.")
        if value > datetime.now(timezone.utc):
            raise ValueError("Eaten timestamp cannot be in the future.")
        return value

    @field_validator("note")
    @classmethod
    def normalize_note(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip() or None


class MealCreate(MealBase):
    pass


class MealUpdate(BaseModel):
    meal_type: MealType | None = None
    eaten_at: datetime | None = None
    note: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_update_fields(self) -> "MealUpdate":
        if not self.model_fields_set:
            raise ValueError("Provide at least one meal field to update.")
        return self

    @field_validator("eaten_at")
    @classmethod
    def validate_eaten_at(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        return MealBase.validate_eaten_at(value)

    @field_validator("note")
    @classmethod
    def normalize_note(cls, value: str | None) -> str | None:
        return MealBase.normalize_note(value)


class MealItemBase(BaseModel):
    food_name: str = Field(min_length=1, max_length=200)
    quantity: Decimal = Field(gt=0, max_digits=10, decimal_places=3)
    unit: FoodUnit
    calories_kcal: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=3)
    protein_g: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=3)
    carbohydrates_g: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=3)
    fat_g: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=3)

    @field_validator("food_name")
    @classmethod
    def normalize_food_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Food name cannot be blank.")
        return normalized


class MealItemCreate(MealItemBase):
    pass


class MealItemUpdate(BaseModel):
    food_name: str | None = Field(default=None, min_length=1, max_length=200)
    quantity: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=3)
    unit: FoodUnit | None = None
    calories_kcal: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=3)
    protein_g: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=3)
    carbohydrates_g: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=3)
    fat_g: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=3)

    @model_validator(mode="after")
    def validate_update_fields(self) -> "MealItemUpdate":
        if not self.model_fields_set:
            raise ValueError("Provide at least one meal item field to update.")
        if "food_name" in self.model_fields_set and self.food_name is None:
            raise ValueError("Food name cannot be null.")
        if ("quantity" in self.model_fields_set) != ("unit" in self.model_fields_set):
            raise ValueError("Quantity and unit must be supplied together.")
        return self

    @field_validator("food_name")
    @classmethod
    def normalize_food_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return MealItemBase.normalize_food_name(value)


class MealItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    food_name: str
    quantity: float
    unit: FoodUnit
    calories_kcal: float | None
    protein_g: float | None
    carbohydrates_g: float | None
    fat_g: float | None
    created_at: datetime
    updated_at: datetime


class MealResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    meal_type: MealType
    eaten_at: datetime
    note: str | None
    created_at: datetime
    updated_at: datetime
    items: list[MealItemResponse]


class MealListResponse(BaseModel):
    items: list[MealResponse]
    total: int
