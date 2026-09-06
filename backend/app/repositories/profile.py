from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.profile import UserProfile


class ProfileRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_profile(self) -> UserProfile | None:
        return self._db.scalar(select(UserProfile).order_by(UserProfile.created_at.asc()).limit(1))

    def add_profile(self, profile: UserProfile) -> None:
        self._db.add(profile)

    def save(self) -> None:
        self._db.commit()
