from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.meal import MealCreate, MealItemCreate, MealItemResponse, MealItemUpdate, MealListResponse, MealResponse, MealUpdate
from app.services.meal import MealItemNotFoundError, MealNotFoundError, MealService

router = APIRouter(prefix="/meals", tags=["meals"])


def meal_not_found(error: MealNotFoundError | MealItemNotFoundError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal or meal item not found.")


@router.get("", response_model=MealListResponse)
def list_meals(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)) -> MealListResponse:
    if not 1 <= limit <= 100 or offset < 0:
        raise HTTPException(status_code=422, detail="Invalid pagination values.")
    return MealService(db).list_meals(limit, offset)


@router.post("", response_model=MealResponse, status_code=status.HTTP_201_CREATED)
def create_meal(payload: MealCreate, db: Session = Depends(get_db)) -> MealResponse:
    return MealService(db).create_meal(payload)


@router.get("/{meal_id}", response_model=MealResponse)
def get_meal(meal_id: UUID, db: Session = Depends(get_db)) -> MealResponse:
    try:
        return MealService(db).get_meal(meal_id)
    except MealNotFoundError as error:
        raise meal_not_found(error) from error


@router.patch("/{meal_id}", response_model=MealResponse)
def update_meal(meal_id: UUID, payload: MealUpdate, db: Session = Depends(get_db)) -> MealResponse:
    try:
        return MealService(db).update_meal(meal_id, payload)
    except MealNotFoundError as error:
        raise meal_not_found(error) from error


@router.delete("/{meal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meal(meal_id: UUID, db: Session = Depends(get_db)) -> Response:
    try:
        MealService(db).delete_meal(meal_id)
    except MealNotFoundError as error:
        raise meal_not_found(error) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{meal_id}/items", response_model=MealItemResponse, status_code=status.HTTP_201_CREATED)
def create_meal_item(meal_id: UUID, payload: MealItemCreate, db: Session = Depends(get_db)) -> MealItemResponse:
    try:
        return MealService(db).create_item(meal_id, payload)
    except MealNotFoundError as error:
        raise meal_not_found(error) from error


@router.patch("/{meal_id}/items/{item_id}", response_model=MealItemResponse)
def update_meal_item(meal_id: UUID, item_id: UUID, payload: MealItemUpdate, db: Session = Depends(get_db)) -> MealItemResponse:
    try:
        return MealService(db).update_item(meal_id, item_id, payload)
    except (MealNotFoundError, MealItemNotFoundError) as error:
        raise meal_not_found(error) from error


@router.delete("/{meal_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meal_item(meal_id: UUID, item_id: UUID, db: Session = Depends(get_db)) -> Response:
    try:
        MealService(db).delete_item(meal_id, item_id)
    except MealItemNotFoundError as error:
        raise meal_not_found(error) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
