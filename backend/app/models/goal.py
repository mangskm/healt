from datetime import date, datetime
from enum import Enum
import uuid

from sqlalchemy import CheckConstraint, Date, DateTime, Enum as SqlEnum, ForeignKey, Index, Numeric, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class GoalType(str, Enum):
    TARGET_WEIGHT = "target_weight"


class GoalStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Goal(Base):
    """A manually managed personal tracking goal stored in canonical kilograms."""

    __tablename__ = "goals"
    __table_args__ = (
        CheckConstraint("target_value_kg > 0", name="ck_goals_target_value_kg_positive"),
        Index("ix_goals_user_status", "user_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    goal_type: Mapped[GoalType] = mapped_column(SqlEnum(GoalType, name="goal_type", native_enum=False, create_constraint=True, values_callable=lambda values: [item.value for item in values]), nullable=False)
    target_value_kg: Mapped[float] = mapped_column(Numeric(10, 3), nullable=False)
    target_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[GoalStatus] = mapped_column(SqlEnum(GoalStatus, name="goal_status", native_enum=False, create_constraint=True, values_callable=lambda values: [item.value for item in values]), nullable=False, default=GoalStatus.ACTIVE)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user: Mapped["User"] = relationship(back_populates="goals")
