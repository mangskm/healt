from fastapi.testclient import TestClient

from app.main import app


def test_unexpected_errors_are_logged_without_sensitive_exception_text(caplog) -> None:
    def broken_endpoint() -> None:
        raise RuntimeError("database password must never reach the client")

    app.add_api_route("/__test-unhandled-error", broken_endpoint)
    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.get("/__test-unhandled-error")
    finally:
        app.router.routes.pop()

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error."}
    assert "RuntimeError" in caplog.text
    assert "database password" not in caplog.text
