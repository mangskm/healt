from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.profile import ProfileResponse, ProfileUpdate
from app.services.profile import ProfileNotFoundError, ProfileService

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileResponse)
def get_profile(db: Session = Depends(get_db)) -> ProfileResponse:
    """Read the single local user's health-profile settings."""
    try:
        return ProfileService(db).get_profile()
    except ProfileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not configured.") from error


@router.patch("", response_model=ProfileResponse)
def update_profile(update: ProfileUpdate, db: Session = Depends(get_db)) -> ProfileResponse:
    """Create or update the single local user's profile fields."""
    return ProfileService(db).update_profile(update)
