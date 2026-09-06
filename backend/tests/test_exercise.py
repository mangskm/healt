from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.models.exercise import ActivityType, ExerciseSession
from app.models.user import User


def payload(**overrides):
    base = {"activity_type": "walking", "performed_at": "2026-09-05T10:00:00Z", "duration_minutes": 45, "distance": 3.5, "distance_unit": "km", "calories_burned_kcal": 180, "note": "  evening walk  "}
    return {**base, **overrides}


def test_exercise_can_be_created_read_and_listed(client: TestClient) -> None:
    created = client.post("/api/v1/exercise-sessions", json=payload())
    session_id = created.json()["id"]
    read = client.get(f"/api/v1/exercise-sessions/{session_id}")
    listed = client.get("/api/v1/exercise-sessions")

    assert created.status_code == 201
    assert created.json()["distance_km"] == 3.5
    assert created.json()["note"] == "evening walk"
    assert read.status_code == 200
    assert listed.json()["total"] == 1


def test_miles_are_converted_to_canonical_kilometers_and_optional_distance_is_supported(client: TestClient) -> None:
    miles = client.post("/api/v1/exercise-sessions", json=payload(distance=3, distance_unit="mi"))
    no_distance = client.post("/api/v1/exercise-sessions", json=payload(activity_type="strength_training", distance=None, distance_unit=None))

    assert miles.json()["distance_km"] == 4.828
    assert no_distance.status_code == 201
    assert no_distance.json()["distance_km"] is None


def test_exercise_order_pagination_update_and_delete(client: TestClient) -> None:
    older = client.post("/api/v1/exercise-sessions", json=payload(performed_at="2026-09-04T10:00:00Z")).json()
    newer = client.post("/api/v1/exercise-sessions", json=payload(activity_type="running", performed_at="2026-09-05T10:00:00Z")).json()
    listed = client.get("/api/v1/exercise-sessions?limit=1&offset=0")
    updated = client.patch(f"/api/v1/exercise-sessions/{older['id']}", json={"duration_minutes": 60, "distance": 2, "distance_unit": "mi"})
    deleted = client.delete(f"/api/v1/exercise-sessions/{older['id']}")

    assert listed.json()["items"][0]["id"] == newer["id"]
    assert listed.json()["total"] == 2
    assert updated.json()["duration_minutes"] == 60
    assert updated.json()["distance_km"] == 3.219
    assert deleted.status_code == 204
    assert client.get(f"/api/v1/exercise-sessions/{older['id']}").status_code == 404


def test_exercise_validates_technical_values(client: TestClient) -> None:
    future = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    invalid_activity = client.post("/api/v1/exercise-sessions", json=payload(activity_type="yoga"))
    invalid_time = client.post("/api/v1/exercise-sessions", json=payload(performed_at="2026-09-05T10:00:00"))
    future_time = client.post("/api/v1/exercise-sessions", json=payload(performed_at=future))
    zero_duration = client.post("/api/v1/exercise-sessions", json=payload(duration_minutes=0))
    invalid_distance = client.post("/api/v1/exercise-sessions", json=payload(distance=0))
    invalid_unit = client.post("/api/v1/exercise-sessions", json=payload(distance_unit="m"))
    negative_calories = client.post("/api/v1/exercise-sessions", json=payload(calories_burned_kcal=-1))
    long_note = client.post("/api/v1/exercise-sessions", json=payload(note="x" * 501))

    assert all(response.status_code == 422 for response in [invalid_activity, invalid_time, future_time, zero_duration, invalid_distance, invalid_unit, negative_calories, long_note])


def test_exercise_sessions_are_scoped_to_the_local_user(client: TestClient, db_session) -> None:
    local = client.post("/api/v1/exercise-sessions", json=payload()).json()
    other_user = User(created_at=datetime(2100, 1, 1, tzinfo=timezone.utc), updated_at=datetime(2100, 1, 1, tzinfo=timezone.utc))
    db_session.add(other_user)
    db_session.flush()
    other = ExerciseSession(user_id=other_user.id, activity_type=ActivityType.RUNNING, performed_at=datetime(2026, 9, 5, tzinfo=timezone.utc), duration_minutes=30)
    db_session.add(other)
    db_session.commit()

    assert client.get("/api/v1/exercise-sessions").json()["items"][0]["id"] == local["id"]
    assert client.get(f"/api/v1/exercise-sessions/{other.id}").status_code == 404
