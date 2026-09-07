from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.exercise import ExerciseCreate, ExerciseListResponse, ExerciseResponse, ExerciseUpdate
from app.services.exercise import ExerciseNotFoundError, ExerciseService

router = APIRouter(prefix="/exercise-sessions", tags=["exercise"])


@router.get("", response_model=ExerciseListResponse)
def list_sessions(limit: int = 50, offset: int = 0, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> ExerciseListResponse:
    if not 1 <= limit <= 100 or offset < 0:
        raise HTTPException(status_code=422, detail="Invalid pagination values.")
    return ExerciseService(db, user).list_sessions(limit, offset)


@router.post("", response_model=ExerciseResponse, status_code=status.HTTP_201_CREATED)
def create_session(payload: ExerciseCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> ExerciseResponse:
    return ExerciseService(db, user).create_session(payload)


@router.get("/{session_id}", response_model=ExerciseResponse)
def get_session(session_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> ExerciseResponse:
    try:
        return ExerciseService(db, user).get_session(session_id)
    except ExerciseNotFoundError as error:
        raise HTTPException(status_code=404, detail="Exercise session not found.") from error


@router.patch("/{session_id}", response_model=ExerciseResponse)
def update_session(session_id: UUID, payload: ExerciseUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> ExerciseResponse:
    try:
        return ExerciseService(db, user).update_session(session_id, payload)
    except ExerciseNotFoundError as error:
        raise HTTPException(status_code=404, detail="Exercise session not found.") from error


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> Response:
    try:
        ExerciseService(db, user).delete_session(session_id)
    except ExerciseNotFoundError as error:
        raise HTTPException(status_code=404, detail="Exercise session not found.") from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
