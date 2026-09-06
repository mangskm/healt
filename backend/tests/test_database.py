from unittest.mock import Mock

import pytest

from app.core import database


def test_get_db_closes_the_session_when_request_handling_raises(monkeypatch) -> None:
    session = Mock()
    monkeypatch.setattr(database, "SessionLocal", lambda: session)

    dependency = database.get_db()
    assert next(dependency) is session

    with pytest.raises(RuntimeError, match="request failed"):
        dependency.throw(RuntimeError("request failed"))

    session.close.assert_called_once_with()


def test_dashboard_and_analytics_can_be_requested_repeatedly(client) -> None:
    endpoints = (
        "/api/v1/dashboard",
        "/api/v1/analytics?period=7d",
        "/api/v1/analytics?period=30d",
    )

    for _ in range(18):
        for endpoint in endpoints:
            assert client.get(endpoint).status_code == 200
