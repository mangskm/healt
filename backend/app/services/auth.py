import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password, hash_session_token, verify_password
from app.models.auth_session import AuthSession
from app.models.user import User
from app.repositories.auth import AuthRepository
from app.schemas.auth import AuthUserResponse


class InvalidCredentialsError(Exception):
    pass


class BootstrapError(Exception):
    pass


class AuthService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repository = AuthRepository(db)

    def login(self, email: str, password: str) -> tuple[AuthUserResponse, str]:
        user = self._repository.get_user_by_email(email)
        if user is None or not user.is_active or user.password_hash is None or not verify_password(user.password_hash, password):
            raise InvalidCredentialsError
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=get_settings().session_ttl_minutes)
        self._repository.add_session(AuthSession(user_id=user.id, token_hash=hash_session_token(token), expires_at=expires_at))
        self._repository.save()
        return AuthUserResponse(id=user.id, email=user.email), token

    def current_user_for_token(self, token: str | None) -> User | None:
        if not token:
            return None
        session = self._repository.get_session_by_token_hash(hash_session_token(token))
        now = datetime.now(timezone.utc)
        if session is None:
            return None
        expires_at = session.expires_at if session.expires_at.tzinfo else session.expires_at.replace(tzinfo=timezone.utc)
        if session.revoked_at is not None or expires_at <= now or not session.user.is_active:
            return None
        return session.user

    def logout(self, token: str | None) -> None:
        if token:
            session = self._repository.get_session_by_token_hash(hash_session_token(token))
            if session is not None and session.revoked_at is None:
                self._repository.revoke_session(session, datetime.now(timezone.utc))
                self._repository.save()

    @staticmethod
    def bootstrap_single_user(db: Session, email: str, password: str) -> User:
        if len(password) < 12:
            raise BootstrapError("Password must contain at least 12 characters.")
        users = list(db.scalars(select(User).order_by(User.created_at.asc())))
        if len(users) > 1:
            raise BootstrapError("Refusing to choose from multiple existing users.")
        if users and (users[0].email is not None or users[0].password_hash is not None):
            raise BootstrapError("The existing user already has credentials.")
        user = users[0] if users else User()
        user.email = email
        user.password_hash = hash_password(password)
        user.is_active = True
        if not users:
            db.add(user)
        db.commit()
        db.refresh(user)
        return user
