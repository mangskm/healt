from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.core.security import hash_password, hash_session_token
from app.models.auth_session import AuthSession
from app.models.user import User
from app.services.auth import AuthService, BootstrapError


def make_user(db_session, email: str = "owner@example.com", password: str = "correct horse battery staple") -> User:
    return AuthService.bootstrap_single_user(db_session, email, password)


def test_protected_endpoints_reject_anonymous_requests(anonymous_client) -> None:
    for path in ("/api/v1/profile", "/api/v1/weight-records", "/api/v1/goals", "/api/v1/meals", "/api/v1/exercise-sessions", "/api/v1/dashboard", "/api/v1/analytics", "/api/v1/reminders", "/api/v1/notifications/today"):
        assert anonymous_client.get(path).status_code == 401
    assert anonymous_client.get("/api/v1/health").status_code == 200


def test_login_creates_httponly_cookie_and_stores_only_hash(db_session, anonymous_client) -> None:
    user = make_user(db_session)
    response = anonymous_client.post("/api/v1/auth/login", json={"email": user.email, "password": "correct horse battery staple"})

    assert response.status_code == 200
    assert response.json()["user"]["id"] == str(user.id)
    assert "HttpOnly" in response.headers["set-cookie"]
    raw_token = anonymous_client.cookies.get("health_session")
    session = db_session.scalar(select(AuthSession))
    assert raw_token
    assert session.token_hash == hash_session_token(raw_token)
    assert raw_token != session.token_hash
    assert session.token_hash != "correct horse battery staple"
    assert user.password_hash != "correct horse battery staple"


def test_login_failure_is_generic_and_me_and_logout_follow_session(db_session, anonymous_client) -> None:
    make_user(db_session)
    wrong_password = anonymous_client.post("/api/v1/auth/login", json={"email": "owner@example.com", "password": "wrong"})
    missing_user = anonymous_client.post("/api/v1/auth/login", json={"email": "missing@example.com", "password": "wrong"})
    login = anonymous_client.post("/api/v1/auth/login", json={"email": "owner@example.com", "password": "correct horse battery staple"})

    assert wrong_password.status_code == missing_user.status_code == 401
    assert wrong_password.json() == missing_user.json() == {"detail": "Invalid email or password."}
    assert login.status_code == 200
    assert anonymous_client.get("/api/v1/auth/me").json()["email"] == "owner@example.com"
    assert anonymous_client.post("/api/v1/auth/logout").status_code == 204
    assert anonymous_client.get("/api/v1/auth/me").status_code == 401
    assert db_session.scalar(select(AuthSession)).revoked_at is not None


def test_expired_session_cannot_access_private_data(db_session, anonymous_client) -> None:
    user = make_user(db_session)
    token = "expired-token"
    db_session.add(AuthSession(user_id=user.id, token_hash=hash_session_token(token), expires_at=datetime.now(timezone.utc) - timedelta(seconds=1)))
    db_session.commit()
    anonymous_client.cookies.set("health_session", token)

    assert anonymous_client.get("/api/v1/dashboard").status_code == 401


def test_ownership_is_enforced_for_another_authenticated_user(client, db_session) -> None:
    created = client.post("/api/v1/weight-records", json={"weight": 70, "unit": "kg", "recorded_at": "2026-09-07T08:00:00Z"})
    other = User(email="other@example.com", password_hash=hash_password("another correct password"))
    db_session.add(other)
    db_session.commit()
    login = client.post("/api/v1/auth/login", json={"email": "other@example.com", "password": "another correct password"})

    assert created.status_code == 201
    assert login.status_code == 200
    assert client.get(f"/api/v1/weight-records/{created.json()['id']}").status_code == 404
    assert client.get("/api/v1/weight-records").json()["total"] == 0


def test_bootstrap_preserves_single_legacy_user_and_refuses_ambiguity(db_session) -> None:
    legacy = User()
    db_session.add(legacy)
    db_session.commit()
    configured = AuthService.bootstrap_single_user(db_session, "legacy@example.com", "safe password")

    assert configured.id == legacy.id
    assert configured.email == "legacy@example.com"
    assert configured.password_hash != "safe password"
    db_session.add(User())
    db_session.commit()
    try:
        AuthService.bootstrap_single_user(db_session, "blocked@example.com", "safe password")
    except BootstrapError:
        pass
    else:
        raise AssertionError("bootstrap must refuse multiple users")


def test_bootstrap_rejects_a_short_password(db_session) -> None:
    try:
        AuthService.bootstrap_single_user(db_session, "owner@example.com", "too-short")
    except BootstrapError as error:
        assert "12" in str(error)
    else:
        raise AssertionError("bootstrap must reject a short password")
