from datetime import date, datetime, time
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.reminder import ReminderScheduleType, ReminderType


def _clean(value: str | None, field: str, maximum: int) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if not value and field == "title":
        raise ValueError("Title cannot be empty.")
    if len(value) > maximum:
        raise ValueError(f"{field.title()} must be at most {maximum} characters.")
    return value or None


class ReminderCreate(BaseModel):
    reminder_type: ReminderType
    title: str = Field(max_length=120)
    reminder_time: time
    schedule_type: ReminderScheduleType
    day_of_week: int | None = Field(default=None, ge=0, le=6)
    enabled: bool = True
    note: str | None = Field(default=None, max_length=500)

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str) -> str:
        return _clean(value, "title", 120) or ""

    @field_validator("note")
    @classmethod
    def clean_note(cls, value: str | None) -> str | None:
        return _clean(value, "note", 500)

    @model_validator(mode="after")
    def validate_schedule(self) -> "ReminderCreate":
        if self.schedule_type is ReminderScheduleType.DAILY and self.day_of_week is not None:
            raise ValueError("Daily reminders must not include a day of week.")
        if self.schedule_type is ReminderScheduleType.WEEKLY and self.day_of_week is None:
            raise ValueError("Weekly reminders require a day of week.")
        return self


class ReminderUpdate(BaseModel):
    reminder_type: ReminderType | None = None
    title: str | None = Field(default=None, max_length=120)
    reminder_time: time | None = None
    schedule_type: ReminderScheduleType | None = None
    day_of_week: int | None = Field(default=None, ge=0, le=6)
    enabled: bool | None = None
    note: str | None = Field(default=None, max_length=500)

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str | None) -> str | None:
        return _clean(value, "title", 120)

    @field_validator("note")
    @classmethod
    def clean_note(cls, value: str | None) -> str | None:
        return _clean(value, "note", 500)

    @model_validator(mode="after")
    def validate_supplied_schedule(self) -> "ReminderUpdate":
        if not self.model_fields_set:
            raise ValueError("Provide at least one reminder field to update.")
        if self.schedule_type is ReminderScheduleType.DAILY and ("day_of_week" not in self.model_fields_set or self.day_of_week is not None):
            raise ValueError("Updating to daily requires day_of_week to be null.")
        if self.schedule_type is ReminderScheduleType.WEEKLY and self.day_of_week is None:
            raise ValueError("Updating to weekly requires a day of week.")
        return self


class ReminderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    reminder_type: ReminderType
    title: str
    reminder_time: time
    schedule_type: ReminderScheduleType
    day_of_week: int | None
    enabled: bool
    note: str | None
    created_at: datetime
    updated_at: datetime


class ReminderListResponse(BaseModel):
    items: list[ReminderResponse]
    total: int


class TodayReminder(BaseModel):
    id: UUID
    reminder_type: ReminderType
    title: str
    reminder_time: time
    schedule_type: ReminderScheduleType
    day_of_week: int | None
    enabled: bool
    status: str


class TodayNotificationsResponse(BaseModel):
    timezone: str
    local_date: date
    reminders: list[TodayReminder]
