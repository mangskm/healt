from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.goal import GoalCreate, GoalListResponse, GoalResponse, GoalUpdate
from app.services.goal import GoalNotFoundError, GoalService

router = APIRouter(prefix="/goals", tags=["goals"])


def goal_not_found(error: GoalNotFoundError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found.")


@router.get("", response_model=GoalListResponse)
def list_goals(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)) -> GoalListResponse:
    if not 1 <= limit <= 100 or offset < 0:
        raise HTTPException(status_code=422, detail="Invalid pagination values.")
    return GoalService(db).list_goals(limit, offset)


@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(payload: GoalCreate, db: Session = Depends(get_db)) -> GoalResponse:
    return GoalService(db).create_goal(payload)


@router.get("/{goal_id}", response_model=GoalResponse)
def get_goal(goal_id: UUID, db: Session = Depends(get_db)) -> GoalResponse:
    try:
        return GoalService(db).get_goal(goal_id)
    except GoalNotFoundError as error:
        raise goal_not_found(error) from error


@router.patch("/{goal_id}", response_model=GoalResponse)
def update_goal(goal_id: UUID, payload: GoalUpdate, db: Session = Depends(get_db)) -> GoalResponse:
    try:
        return GoalService(db).update_goal(goal_id, payload)
    except GoalNotFoundError as error:
        raise goal_not_found(error) from error


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(goal_id: UUID, db: Session = Depends(get_db)) -> Response:
    try:
        GoalService(db).delete_goal(goal_id)
    except GoalNotFoundError as error:
        raise goal_not_found(error) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
