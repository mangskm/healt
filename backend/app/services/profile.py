from sqlalchemy.orm import Session

from app.models.profile import UserProfile
from app.models.user import User
from app.repositories.profile import ProfileRepository
from app.schemas.profile import ProfileResponse, ProfileUpdate


class ProfileNotFoundError(Exception):
    """Raised when the local profile has not been configured yet."""


class ProfileService:
    def __init__(self, db: Session, user: User) -> None:
        self._db = db
        self._user = user
        self._repository = ProfileRepository(db)

    def get_profile(self) -> ProfileResponse:
        profile = self._repository.get_for_user(self._user.id)
        if profile is None:
            raise ProfileNotFoundError
        return ProfileResponse.model_validate(profile)

    def update_profile(self, update: ProfileUpdate) -> ProfileResponse:
        profile = self._repository.get_for_user(self._user.id)
        if profile is None:
            profile = UserProfile(user_id=self._user.id)
            self._repository.add_profile(profile)
        for field_name, value in update.model_dump(exclude_unset=True).items():
            setattr(profile, field_name, value)
        self._repository.save()
        self._db.refresh(profile)
        return ProfileResponse.model_validate(profile)
