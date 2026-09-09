from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.auth_session import AuthSession
from app.models.user import User


class AuthRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_user_by_email(self, email: str) -> User | None:
        return self._db.scalar(select(User).where(User.email == email))

    def get_session_by_token_hash(self, token_hash: str) -> AuthSession | None:
        return self._db.scalar(select(AuthSession).options(joinedload(AuthSession.user)).where(AuthSession.token_hash == token_hash))

    def add_session(self, session: AuthSession) -> None:
        self._db.add(session)

    def revoke_session(self, session: AuthSession, now: datetime) -> None:
        session.revoked_at = now

    def save(self) -> None:
        self._db.commit()
