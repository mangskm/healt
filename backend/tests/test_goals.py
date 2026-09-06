from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.models.goal import Goal
from app.models.user import User


def create_goal(client: TestClient, *, value: float = 150, unit: str = "lb"):
    return client.post("/api/v1/goals", json={"goal_type": "target_weight", "target_value": value, "unit": unit, "target_date": "2027-01-01"})


def test_goal_can_be_created_listed_and_read(client: TestClient) -> None:
    create_response = create_goal(client)
    goal_id = create_response.json()["id"]
    list_response = client.get("/api/v1/goals")
    read_response = client.get(f"/api/v1/goals/{goal_id}")

    assert create_response.status_code == 201
    assert create_response.json()["target_value_kg"] == 68.039
    assert create_response.json()["status"] == "active"
    assert list_response.json()["total"] == 1
    assert read_response.status_code == 200


def test_goal_can_be_updated_cancelled_and_deleted(client: TestClient) -> None:
    goal_id = create_goal(client, value=70, unit="kg").json()["id"]
    update_response = client.patch(f"/api/v1/goals/{goal_id}", json={"target_value": 160, "unit": "lb", "status": "cancelled"})
    delete_response = client.delete(f"/api/v1/goals/{goal_id}")
    read_response = client.get(f"/api/v1/goals/{goal_id}")

    assert update_response.status_code == 200
    assert update_response.json()["target_value_kg"] == 72.575
    assert update_response.json()["status"] == "cancelled"
    assert delete_response.status_code == 204
    assert read_response.status_code == 404


def test_goal_rejects_invalid_values_and_partial_unit_updates(client: TestClient) -> None:
    invalid_create = client.post("/api/v1/goals", json={"goal_type": "food", "target_value": 0, "unit": "stone"})
    incomplete_update = client.patch("/api/v1/goals/00000000-0000-0000-0000-000000000001", json={"target_value": 70})

    assert invalid_create.status_code == 422
    assert incomplete_update.status_code == 422


def test_goals_do_not_expose_another_users_data(client: TestClient, db_session) -> None:
    local_goal = create_goal(client, value=70, unit="kg")
    other_user = User(created_at=datetime(2100, 1, 1, tzinfo=timezone.utc), updated_at=datetime(2100, 1, 1, tzinfo=timezone.utc))
    db_session.add(other_user)
    db_session.flush()
    other_goal = Goal(user_id=other_user.id, goal_type="target_weight", target_value_kg=60, status="active")
    db_session.add(other_goal)
    db_session.commit()

    list_response = client.get("/api/v1/goals")
    other_response = client.get(f"/api/v1/goals/{other_goal.id}")

    assert list_response.json()["total"] == 1
    assert list_response.json()["items"][0]["id"] == local_goal.json()["id"]
    assert other_response.status_code == 404
