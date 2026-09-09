from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.profile import ProfileResponse, ProfileUpdate
from app.services.profile import ProfileNotFoundError, ProfileService

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileResponse)
def get_profile(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> ProfileResponse:
    """Read the single local user's health-profile settings."""
    try:
        return ProfileService(db, user).get_profile()
    except ProfileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not configured.") from error


@router.patch("", response_model=ProfileResponse)
def update_profile(update: ProfileUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> ProfileResponse:
    """Create or update the single local user's profile fields."""
    return ProfileService(db, user).update_profile(update)
