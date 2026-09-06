from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.exercise import ActivityType, DistanceUnit


class ExerciseBase(BaseModel):
    activity_type: ActivityType
    performed_at: datetime
    duration_minutes: int = Field(gt=0)
    distance: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=3)
    distance_unit: DistanceUnit | None = None
    calories_burned_kcal: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=3)
    note: str | None = Field(default=None, max_length=500)

    @field_validator("performed_at")
    @classmethod
    def validate_performed_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Performed timestamp must include a timezone.")
        if value > datetime.now(timezone.utc):
            raise ValueError("Performed timestamp cannot be in the future.")
        return value

    @field_validator("note")
    @classmethod
    def normalize_note(cls, value: str | None) -> str | None:
        return value.strip() or None if value is not None else None

    @model_validator(mode="after")
    def validate_distance(self) -> "ExerciseBase":
        if (self.distance is None) != (self.distance_unit is None):
            raise ValueError("Distance and distance unit must be supplied together.")
        return self


class ExerciseCreate(ExerciseBase):
    pass


class ExerciseUpdate(BaseModel):
    activity_type: ActivityType | None = None
    performed_at: datetime | None = None
    duration_minutes: int | None = Field(default=None, gt=0)
    distance: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=3)
    distance_unit: DistanceUnit | None = None
    calories_burned_kcal: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=3)
    note: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_update(self) -> "ExerciseUpdate":
        if not self.model_fields_set:
            raise ValueError("Provide at least one exercise session field to update.")
        if ("distance" in self.model_fields_set) != ("distance_unit" in self.model_fields_set):
            raise ValueError("Distance and distance unit must be supplied together.")
        return self

    @field_validator("performed_at")
    @classmethod
    def validate_performed_at(cls, value: datetime | None) -> datetime | None:
        return ExerciseBase.validate_performed_at(value) if value is not None else None

    @field_validator("note")
    @classmethod
    def normalize_note(cls, value: str | None) -> str | None:
        return ExerciseBase.normalize_note(value)


class ExerciseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    activity_type: ActivityType
    performed_at: datetime
    duration_minutes: int
    distance_km: float | None
    calories_burned_kcal: float | None
    note: str | None
    created_at: datetime
    updated_at: datetime


class ExerciseListResponse(BaseModel):
    items: list[ExerciseResponse]
    total: int
