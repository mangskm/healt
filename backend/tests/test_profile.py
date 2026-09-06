from fastapi.testclient import TestClient


def test_profile_is_not_found_before_initial_setup(client: TestClient) -> None:
    response = client.get("/api/v1/profile")

    assert response.status_code == 404
    assert response.json() == {"detail": "Profile not configured."}


def test_profile_can_be_created_and_read(client: TestClient) -> None:
    payload = {
        "preferred_name": "Mali",
        "date_of_birth": "1998-04-12",
        "sex": "female",
        "height_cm": 165.5,
        "weight_unit": "kg",
        "height_unit": "cm",
        "timezone": "Asia/Bangkok",
    }

    update_response = client.patch("/api/v1/profile", json=payload)
    read_response = client.get("/api/v1/profile")

    assert update_response.status_code == 200
    assert update_response.json()["preferred_name"] == "Mali"
    assert update_response.json()["height_cm"] == 165.5
    assert read_response.status_code == 200
    assert read_response.json()["timezone"] == "Asia/Bangkok"


def test_profile_partial_update_preserves_unspecified_values(client: TestClient) -> None:
    client.patch("/api/v1/profile", json={"preferred_name": "Mali", "weight_unit": "kg"})

    response = client.patch("/api/v1/profile", json={"weight_unit": "lb"})

    assert response.status_code == 200
    assert response.json()["preferred_name"] == "Mali"
    assert response.json()["weight_unit"] == "lb"


def test_profile_rejects_invalid_health_profile_values(client: TestClient) -> None:
    response = client.patch(
        "/api/v1/profile",
        json={"height_cm": 310, "date_of_birth": "2999-01-01", "timezone": "not-a-timezone"},
    )

    assert response.status_code == 422
