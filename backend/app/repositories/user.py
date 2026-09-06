from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """Temporary local-owner lookup, to be replaced by authenticated identity later."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_or_create_local_user(self) -> User:
        user = self._db.scalar(select(User).order_by(User.created_at.asc()).limit(1))
        if user is not None:
            return user
        user = User()
        self._db.add(user)
        self._db.flush()
        return user
