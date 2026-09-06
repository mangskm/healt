from datetime import datetime
from enum import Enum
import uuid

from sqlalchemy import CheckConstraint, DateTime, Enum as SqlEnum, ForeignKey, Index, Integer, Numeric, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ActivityType(str, Enum):
    WALKING = "walking"
    RUNNING = "running"
    CYCLING = "cycling"
    STRENGTH_TRAINING = "strength_training"
    SWIMMING = "swimming"
    SPORTS = "sports"
    OTHER = "other"


class DistanceUnit(str, Enum):
    KILOMETERS = "km"
    MILES = "mi"


class ExerciseSession(Base):
    """A manually recorded exercise or activity session."""

    __tablename__ = "exercise_sessions"
    __table_args__ = (
        CheckConstraint("duration_minutes > 0", name="ck_exercise_sessions_duration_positive"),
        CheckConstraint("distance_km IS NULL OR distance_km > 0", name="ck_exercise_sessions_distance_positive"),
        CheckConstraint("calories_burned_kcal IS NULL OR calories_burned_kcal >= 0", name="ck_exercise_sessions_calories_non_negative"),
        Index("ix_exercise_sessions_user_performed_at", "user_id", "performed_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    activity_type: Mapped[ActivityType] = mapped_column(SqlEnum(ActivityType, name="activity_type", native_enum=False, create_constraint=True, values_callable=lambda values: [item.value for item in values]), nullable=False)
    performed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    distance_km: Mapped[float | None] = mapped_column(Numeric(10, 3))
    calories_burned_kcal: Mapped[float | None] = mapped_column(Numeric(10, 3))
    note: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user: Mapped["User"] = relationship(back_populates="exercise_sessions")
