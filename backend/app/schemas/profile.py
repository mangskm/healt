from datetime import date, datetime
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.profile import HeightUnit, Sex, WeightUnit


class ProfileUpdate(BaseModel):
    """Fields that can be updated independently; explicit null clears a saved value."""

    preferred_name: str | None = Field(default=None, max_length=80)
    date_of_birth: date | None = None
    sex: Sex | None = None
    height_cm: float | None = Field(default=None, ge=50, le=300)
    weight_unit: WeightUnit | None = None
    height_unit: HeightUnit | None = None
    timezone: str | None = Field(default=None, max_length=64)

    @model_validator(mode="after")
    def has_an_explicit_update(self) -> "ProfileUpdate":
        if not self.model_fields_set:
            raise ValueError("Provide at least one profile field to update.")
        return self

    @field_validator("preferred_name")
    @classmethod
    def validate_preferred_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("Preferred name cannot be blank.")
        return normalized

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, value: date | None) -> date | None:
        if value is not None and value > date.today():
            raise ValueError("Date of birth cannot be in the future.")
        return value

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("Timezone cannot be blank.")
        try:
            ZoneInfo(normalized)
        except ZoneInfoNotFoundError as error:
            raise ValueError("Timezone must be a valid IANA timezone.") from error
        return normalized


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    preferred_name: str | None
    date_of_birth: date | None
    sex: Sex | None
    height_cm: float | None
    weight_unit: WeightUnit | None
    height_unit: HeightUnit | None
    timezone: str | None
    created_at: datetime
    updated_at: datetime
