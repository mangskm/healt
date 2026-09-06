from datetime import datetime
from enum import Enum
import uuid

from sqlalchemy import CheckConstraint, DateTime, Enum as SqlEnum, ForeignKey, Index, Numeric, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class MealType(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
    OTHER = "other"


class FoodUnit(str, Enum):
    GRAM = "g"
    MILLILITRE = "ml"
    SERVING = "serving"
    PIECE = "piece"


class Meal(Base):
    """One manual eating event for a user."""

    __tablename__ = "meals"
    __table_args__ = (Index("ix_meals_user_eaten_at", "user_id", "eaten_at"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    meal_type: Mapped[MealType] = mapped_column(SqlEnum(MealType, name="meal_type", native_enum=False, create_constraint=True, values_callable=lambda values: [item.value for item in values]), nullable=False)
    eaten_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    note: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user: Mapped["User"] = relationship(back_populates="meals")
    items: Mapped[list["MealItem"]] = relationship(back_populates="meal", cascade="all, delete-orphan", passive_deletes=True)


class MealItem(Base):
    """A manually entered food amount belonging to one meal."""

    __tablename__ = "meal_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_meal_items_quantity_positive"),
        CheckConstraint("calories_kcal IS NULL OR calories_kcal >= 0", name="ck_meal_items_calories_non_negative"),
        CheckConstraint("protein_g IS NULL OR protein_g >= 0", name="ck_meal_items_protein_non_negative"),
        CheckConstraint("carbohydrates_g IS NULL OR carbohydrates_g >= 0", name="ck_meal_items_carbohydrates_non_negative"),
        CheckConstraint("fat_g IS NULL OR fat_g >= 0", name="ck_meal_items_fat_non_negative"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    meal_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("meals.id", ondelete="CASCADE"), nullable=False)
    food_name: Mapped[str] = mapped_column(String(200), nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(10, 3), nullable=False)
    unit: Mapped[FoodUnit] = mapped_column(SqlEnum(FoodUnit, name="food_unit", native_enum=False, create_constraint=True, values_callable=lambda values: [item.value for item in values]), nullable=False)
    calories_kcal: Mapped[float | None] = mapped_column(Numeric(10, 3))
    protein_g: Mapped[float | None] = mapped_column(Numeric(10, 3))
    carbohydrates_g: Mapped[float | None] = mapped_column(Numeric(10, 3))
    fat_g: Mapped[float | None] = mapped_column(Numeric(10, 3))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    meal: Mapped[Meal] = relationship(back_populates="items")
