from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.config import get_settings
from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import AuthUserResponse, LoginRequest, LoginResponse
from app.services.auth import AuthService, InvalidCredentialsError

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> LoginResponse:
    try:
        user, token = AuthService(db).login(payload.email, payload.password)
    except InvalidCredentialsError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.") from error
    settings = get_settings()
    response.set_cookie(key=settings.session_cookie_name, value=token, httponly=True, secure=settings.session_cookie_secure, samesite="lax", path="/", max_age=settings.session_ttl_seconds)
    return LoginResponse(user=user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, db: Session = Depends(get_db)) -> Response:
    settings = get_settings()
    AuthService(db).logout(request.cookies.get(settings.session_cookie_name))
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie(key=settings.session_cookie_name, path="/")
    return response


@router.get("/me", response_model=AuthUserResponse)
def me(user: User = Depends(get_current_user)) -> AuthUserResponse:
    return AuthUserResponse(id=user.id, email=user.email)
