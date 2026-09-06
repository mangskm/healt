import uuid
from datetime import datetime, time
from enum import Enum

from sqlalchemy import Boolean, CheckConstraint, DateTime, Enum as SqlEnum, ForeignKey, Index, Integer, String, Time, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ReminderType(str, Enum):
    WEIGHT = "weight"
    MEAL = "meal"
    EXERCISE = "exercise"
    CUSTOM = "custom"


class ReminderScheduleType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"


class Reminder(Base):
    __tablename__ = "reminders"
    __table_args__ = (
        CheckConstraint("day_of_week IS NULL OR (day_of_week >= 0 AND day_of_week <= 6)", name="ck_reminders_day_of_week_range"),
        CheckConstraint("(schedule_type = 'daily' AND day_of_week IS NULL) OR (schedule_type = 'weekly' AND day_of_week IS NOT NULL)", name="ck_reminders_schedule_day"),
        Index("ix_reminders_user_enabled_time", "user_id", "enabled", "reminder_time"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reminder_type: Mapped[ReminderType] = mapped_column(SqlEnum(ReminderType, name="reminder_type", native_enum=False, create_constraint=True, values_callable=lambda items: [item.value for item in items]), nullable=False)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    reminder_time: Mapped[time] = mapped_column(Time(), nullable=False)
    schedule_type: Mapped[ReminderScheduleType] = mapped_column(SqlEnum(ReminderScheduleType, name="reminder_schedule_type", native_enum=False, create_constraint=True, values_callable=lambda items: [item.value for item in items]), nullable=False)
    day_of_week: Mapped[int | None] = mapped_column(Integer)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    note: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user: Mapped["User"] = relationship(back_populates="reminders")
