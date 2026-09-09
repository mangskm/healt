from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.reminder import ReminderCreate, ReminderListResponse, ReminderResponse, ReminderUpdate, TodayNotificationsResponse
from app.services.reminder import ReminderNotFoundError, ReminderService

router = APIRouter(prefix="/reminders", tags=["reminders"])
notifications_router = APIRouter(prefix="/notifications", tags=["notifications"])


def missing(error: Exception) -> HTTPException:
    return HTTPException(status_code=404, detail="Reminder not found.")


@router.get("", response_model=ReminderListResponse)
def list_reminders(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> ReminderListResponse:
    return ReminderService(db, user).list_reminders()


@router.post("", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
def create_reminder(payload: ReminderCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> ReminderResponse:
    return ReminderService(db, user).create_reminder(payload)


@router.get("/{reminder_id}", response_model=ReminderResponse)
def get_reminder(reminder_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> ReminderResponse:
    try:
        return ReminderService(db, user).get_reminder(reminder_id)
    except ReminderNotFoundError as error:
        raise missing(error) from error


@router.patch("/{reminder_id}", response_model=ReminderResponse)
def update_reminder(reminder_id: UUID, payload: ReminderUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> ReminderResponse:
    try:
        return ReminderService(db, user).update_reminder(reminder_id, payload)
    except ReminderNotFoundError as error:
        raise missing(error) from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reminder(reminder_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> Response:
    try:
        ReminderService(db, user).delete_reminder(reminder_id)
    except ReminderNotFoundError as error:
        raise missing(error) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@notifications_router.get("/today", response_model=TodayNotificationsResponse)
def today_notifications(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> TodayNotificationsResponse:
    return ReminderService(db, user).today()
