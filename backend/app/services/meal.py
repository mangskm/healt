from uuid import UUID

from sqlalchemy.orm import Session

from app.models.meal import Meal, MealItem
from app.repositories.meal import MealRepository
from app.repositories.user import UserRepository
from app.schemas.meal import MealCreate, MealItemCreate, MealItemResponse, MealItemUpdate, MealListResponse, MealResponse, MealUpdate


class MealNotFoundError(Exception):
    """Raised for a missing or non-owned meal."""


class MealItemNotFoundError(Exception):
    """Raised for a missing or non-owned meal item."""


class MealService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._users = UserRepository(db)
        self._meals = MealRepository(db)

    def list_meals(self, limit: int, offset: int) -> MealListResponse:
        user = self._users.get_or_create_local_user()
        meals, total = self._meals.list_for_user(user.id, limit, offset)
        return MealListResponse(items=[MealResponse.model_validate(meal) for meal in meals], total=total)

    def get_meal(self, meal_id: UUID) -> MealResponse:
        return MealResponse.model_validate(self._get_owned_meal(meal_id))

    def create_meal(self, payload: MealCreate) -> MealResponse:
        user = self._users.get_or_create_local_user()
        meal = Meal(user_id=user.id, **payload.model_dump())
        self._meals.add(meal)
        self._meals.save()
        return self.get_meal(meal.id)

    def update_meal(self, meal_id: UUID, payload: MealUpdate) -> MealResponse:
        meal = self._get_owned_meal(meal_id)
        for field_name, value in payload.model_dump(exclude_unset=True).items():
            setattr(meal, field_name, value)
        self._meals.save()
        return self.get_meal(meal.id)

    def delete_meal(self, meal_id: UUID) -> None:
        meal = self._get_owned_meal(meal_id)
        self._meals.delete(meal)
        self._meals.save()

    def create_item(self, meal_id: UUID, payload: MealItemCreate) -> MealItemResponse:
        meal = self._get_owned_meal(meal_id)
        item = MealItem(meal_id=meal.id, **payload.model_dump())
        self._meals.add(item)
        self._meals.save()
        self._db.refresh(item)
        return MealItemResponse.model_validate(item)

    def update_item(self, meal_id: UUID, item_id: UUID, payload: MealItemUpdate) -> MealItemResponse:
        item = self._get_owned_item(meal_id, item_id)
        for field_name, value in payload.model_dump(exclude_unset=True).items():
            setattr(item, field_name, value)
        self._meals.save()
        self._db.refresh(item)
        return MealItemResponse.model_validate(item)

    def delete_item(self, meal_id: UUID, item_id: UUID) -> None:
        item = self._get_owned_item(meal_id, item_id)
        self._meals.delete(item)
        self._meals.save()

    def _get_owned_meal(self, meal_id: UUID) -> Meal:
        user = self._users.get_or_create_local_user()
        meal = self._meals.get_for_user(user.id, meal_id)
        if meal is None:
            raise MealNotFoundError
        return meal

    def _get_owned_item(self, meal_id: UUID, item_id: UUID) -> MealItem:
        user = self._users.get_or_create_local_user()
        item = self._meals.get_item_for_user(user.id, meal_id, item_id)
        if item is None:
            raise MealItemNotFoundError
        return item
