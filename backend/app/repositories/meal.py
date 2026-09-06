from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.meal import Meal, MealItem


class MealRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_for_user(self, user_id: UUID, limit: int, offset: int) -> tuple[list[Meal], int]:
        statement = select(Meal).options(selectinload(Meal.items)).where(Meal.user_id == user_id).order_by(Meal.eaten_at.desc(), Meal.created_at.desc()).limit(limit).offset(offset)
        meals = list(self._db.scalars(statement))
        total = self._db.scalar(select(func.count()).select_from(Meal).where(Meal.user_id == user_id)) or 0
        return meals, total

    def get_for_user(self, user_id: UUID, meal_id: UUID) -> Meal | None:
        statement = select(Meal).options(selectinload(Meal.items)).where(Meal.user_id == user_id, Meal.id == meal_id)
        return self._db.scalar(statement)

    def get_item_for_user(self, user_id: UUID, meal_id: UUID, item_id: UUID) -> MealItem | None:
        statement = select(MealItem).join(Meal).where(Meal.user_id == user_id, Meal.id == meal_id, MealItem.id == item_id)
        return self._db.scalar(statement)

    def add(self, entity: Meal | MealItem) -> None:
        self._db.add(entity)

    def delete(self, entity: Meal | MealItem) -> None:
        self._db.delete(entity)

    def save(self) -> None:
        self._db.commit()
