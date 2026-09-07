from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.goal import GoalCreate, GoalListResponse, GoalResponse, GoalUpdate
from app.services.goal import GoalNotFoundError, GoalService

router = APIRouter(prefix="/goals", tags=["goals"])


def goal_not_found(error: GoalNotFoundError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found.")


@router.get("", response_model=GoalListResponse)
def list_goals(limit: int = 50, offset: int = 0, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> GoalListResponse:
    if not 1 <= limit <= 100 or offset < 0:
        raise HTTPException(status_code=422, detail="Invalid pagination values.")
    return GoalService(db, user).list_goals(limit, offset)


@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(payload: GoalCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> GoalResponse:
    return GoalService(db, user).create_goal(payload)


@router.get("/{goal_id}", response_model=GoalResponse)
def get_goal(goal_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> GoalResponse:
    try:
        return GoalService(db, user).get_goal(goal_id)
    except GoalNotFoundError as error:
        raise goal_not_found(error) from error


@router.patch("/{goal_id}", response_model=GoalResponse)
def update_goal(goal_id: UUID, payload: GoalUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> GoalResponse:
    try:
        return GoalService(db, user).update_goal(goal_id, payload)
    except GoalNotFoundError as error:
        raise goal_not_found(error) from error


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(goal_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> Response:
    try:
        GoalService(db, user).delete_goal(goal_id)
    except GoalNotFoundError as error:
        raise goal_not_found(error) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
