from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.models.user import User
from app.models.weight import WeightRecord


def create_record(client: TestClient, *, weight: float = 70, unit: str = "kg", recorded_at: str = "2026-01-10T08:30:00Z"):
    return client.post("/api/v1/weight-records", json={"weight": weight, "unit": unit, "recorded_at": recorded_at, "note": "Morning"})


def test_weight_record_can_be_created_and_read(client: TestClient) -> None:
    create_response = create_record(client, weight=150, unit="lb")
    record_id = create_response.json()["id"]
    read_response = client.get(f"/api/v1/weight-records/{record_id}")

    assert create_response.status_code == 201
    assert create_response.json()["weight_kg"] == 68.039
    assert read_response.status_code == 200
    assert read_response.json()["note"] == "Morning"


def test_records_are_listed_by_measurement_time_with_latest(client: TestClient) -> None:
    earlier = create_record(client, recorded_at="2026-01-10T08:30:00Z")
    latest = create_record(client, weight=71, recorded_at="2026-08-10T08:30:00Z")

    response = client.get("/api/v1/weight-records?limit=50&offset=0")

    assert response.status_code == 200
    assert response.json()["total"] == 2
    assert response.json()["items"][0]["id"] == latest.json()["id"]
    assert response.json()["latest"]["id"] == latest.json()["id"]
    assert response.json()["items"][1]["id"] == earlier.json()["id"]


def test_weight_record_can_be_updated_and_deleted(client: TestClient) -> None:
    record_id = create_record(client).json()["id"]
    update_response = client.patch(f"/api/v1/weight-records/{record_id}", json={"weight": 160, "unit": "lb", "note": "Updated"})
    delete_response = client.delete(f"/api/v1/weight-records/{record_id}")
    read_response = client.get(f"/api/v1/weight-records/{record_id}")

    assert update_response.status_code == 200
    assert update_response.json()["weight_kg"] == 72.575
    assert update_response.json()["note"] == "Updated"
    assert delete_response.status_code == 204
    assert read_response.status_code == 404


def test_weight_record_rejects_invalid_input(client: TestClient) -> None:
    response = client.post("/api/v1/weight-records", json={"weight": 0, "unit": "stone", "recorded_at": "2999-01-01T00:00:00Z"})
    incomplete_update = client.patch("/api/v1/weight-records/00000000-0000-0000-0000-000000000001", json={"weight": 70})

    assert response.status_code == 422
    assert incomplete_update.status_code == 422


def test_weight_records_do_not_expose_another_users_data(client: TestClient, db_session) -> None:
    local_record = create_record(client)
    other_user = User(created_at=datetime(2100, 1, 1, tzinfo=timezone.utc), updated_at=datetime(2100, 1, 1, tzinfo=timezone.utc))
    db_session.add(other_user)
    db_session.flush()
    other_record = WeightRecord(user_id=other_user.id, weight_kg=99, recorded_at=datetime(2026, 2, 1, tzinfo=timezone.utc))
    db_session.add(other_record)
    db_session.commit()

    list_response = client.get("/api/v1/weight-records")
    other_response = client.get(f"/api/v1/weight-records/{other_record.id}")

    assert list_response.status_code == 200
    assert list_response.json()["total"] == 1
    assert list_response.json()["items"][0]["id"] == local_record.json()["id"]
    assert other_response.status_code == 404
