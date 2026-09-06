from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.profile import WeightUnit


class WeightRecordBase(BaseModel):
    weight: Decimal = Field(gt=0, max_digits=10, decimal_places=3)
    unit: WeightUnit
    recorded_at: datetime
    note: str | None = Field(default=None, max_length=500)

    @field_validator("recorded_at")
    @classmethod
    def validate_recorded_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Recorded timestamp must include a timezone.")
        if value > datetime.now(timezone.utc):
            raise ValueError("Recorded timestamp cannot be in the future.")
        return value

    @field_validator("note")
    @classmethod
    def normalize_note(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class WeightRecordCreate(WeightRecordBase):
    pass


class WeightRecordUpdate(BaseModel):
    weight: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=3)
    unit: WeightUnit | None = None
    recorded_at: datetime | None = None
    note: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_update_fields(self) -> "WeightRecordUpdate":
        if not self.model_fields_set:
            raise ValueError("Provide at least one weight record field to update.")
        includes_weight = "weight" in self.model_fields_set
        includes_unit = "unit" in self.model_fields_set
        if includes_weight != includes_unit:
            raise ValueError("Weight and unit must be supplied together.")
        return self

    @field_validator("recorded_at")
    @classmethod
    def validate_recorded_at(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        return WeightRecordBase.validate_recorded_at(value)

    @field_validator("note")
    @classmethod
    def normalize_note(cls, value: str | None) -> str | None:
        return WeightRecordBase.normalize_note(value)


class WeightRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    weight_kg: float
    recorded_at: datetime
    note: str | None
    created_at: datetime
    updated_at: datetime


class WeightRecordListResponse(BaseModel):
    items: list[WeightRecordResponse]
    total: int
    latest: WeightRecordResponse | None
