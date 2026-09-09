from fastapi.testclient import TestClient


def test_health_endpoint_reports_api_and_database_status(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected"}


def test_live_and_ready_endpoints_are_safe(client: TestClient) -> None:
    live = client.get("/api/v1/live")
    ready = client.get("/api/v1/ready")

    assert live.status_code == 200
    assert live.json() == {"status": "ok"}
    assert ready.status_code == 200
    assert ready.json() == {"status": "ok", "database": "connected"}
