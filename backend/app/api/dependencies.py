from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.models.user import User
from app.services.auth import AuthService


def get_current_user(
    db: Session = Depends(get_db),
    session_token: Annotated[str | None, Cookie(alias=get_settings().session_cookie_name)] = None,
) -> User:
    user = AuthService(db).current_user_for_token(session_token)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")
    return user
