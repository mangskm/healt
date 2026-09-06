from datetime import date, datetime
from enum import Enum
import uuid

from sqlalchemy import Date, DateTime, Enum as SqlEnum, ForeignKey, Numeric, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Sex(str, Enum):
    FEMALE = "female"
    MALE = "male"
    INTERSEX = "intersex"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class WeightUnit(str, Enum):
    KILOGRAMS = "kg"
    POUNDS = "lb"


class HeightUnit(str, Enum):
    CENTIMETERS = "cm"
    FEET_AND_INCHES = "ft_in"


class UserProfile(Base):
    """Non-diagnostic personal settings and baseline measurements."""

    __tablename__ = "user_profiles"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    preferred_name: Mapped[str | None] = mapped_column(String(80))
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    sex: Mapped[Sex | None] = mapped_column(SqlEnum(Sex, name="profile_sex", native_enum=False, create_constraint=True, values_callable=lambda values: [item.value for item in values]))
    height_cm: Mapped[float | None] = mapped_column(Numeric(5, 2))
    weight_unit: Mapped[WeightUnit | None] = mapped_column(SqlEnum(WeightUnit, name="weight_unit", native_enum=False, create_constraint=True, values_callable=lambda values: [item.value for item in values]))
    height_unit: Mapped[HeightUnit | None] = mapped_column(SqlEnum(HeightUnit, name="height_unit", native_enum=False, create_constraint=True, values_callable=lambda values: [item.value for item in values]))
    timezone: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    user: Mapped["User"] = relationship(back_populates="profile")
