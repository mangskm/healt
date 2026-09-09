from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.profile import UserProfile


class ProfileRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_for_user(self, user_id) -> UserProfile | None:
        return self._db.scalar(select(UserProfile).where(UserProfile.user_id == user_id))

    def add_profile(self, profile: UserProfile) -> None:
        self._db.add(profile)

    def save(self) -> None:
        self._db.commit()
