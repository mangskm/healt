from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.models.meal import FoodUnit, Meal, MealItem, MealType
from app.models.user import User


def meal_payload(*, meal_type: str = "lunch", eaten_at: str = "2026-09-06T10:00:00Z") -> dict:
    return {"meal_type": meal_type, "eaten_at": eaten_at, "note": "  packed lunch  "}


def item_payload(*, name: str = "Rice", quantity: float = 150, unit: str = "g") -> dict:
    return {"food_name": name, "quantity": quantity, "unit": unit, "calories_kcal": 240, "protein_g": 4.5, "carbohydrates_g": 52, "fat_g": 0.5}


def test_meal_with_multiple_items_can_be_created_listed_and_read(client: TestClient) -> None:
    created = client.post("/api/v1/meals", json=meal_payload())
    meal_id = created.json()["id"]
    first_item = client.post(f"/api/v1/meals/{meal_id}/items", json=item_payload())
    second_item = client.post(f"/api/v1/meals/{meal_id}/items", json=item_payload(name="Tofu", quantity=100, unit="g"))
    listed = client.get("/api/v1/meals")
    read = client.get(f"/api/v1/meals/{meal_id}")

    assert created.status_code == 201
    assert created.json()["note"] == "packed lunch"
    assert first_item.status_code == 201
    assert second_item.status_code == 201
    assert listed.json()["total"] == 1
    assert [item["food_name"] for item in read.json()["items"]] == ["Rice", "Tofu"]


def test_meals_are_ordered_paginated_and_can_be_updated(client: TestClient) -> None:
    older = client.post("/api/v1/meals", json=meal_payload(eaten_at="2026-09-05T10:00:00Z")).json()
    newer = client.post("/api/v1/meals", json=meal_payload(meal_type="dinner", eaten_at="2026-09-06T10:00:00Z")).json()
    listed = client.get("/api/v1/meals?limit=1&offset=0")
    updated = client.patch(f"/api/v1/meals/{older['id']}", json={"meal_type": "breakfast", "note": None})

    assert listed.status_code == 200
    assert listed.json()["total"] == 2
    assert listed.json()["items"][0]["id"] == newer["id"]
    assert updated.json()["meal_type"] == "breakfast"
    assert updated.json()["note"] is None


def test_meal_item_can_be_updated_and_deleted(client: TestClient) -> None:
    meal_id = client.post("/api/v1/meals", json=meal_payload()).json()["id"]
    item_id = client.post(f"/api/v1/meals/{meal_id}/items", json=item_payload()).json()["id"]
    updated = client.patch(f"/api/v1/meals/{meal_id}/items/{item_id}", json={"food_name": "Brown rice", "quantity": 125, "unit": "g", "calories_kcal": 200})
    deleted = client.delete(f"/api/v1/meals/{meal_id}/items/{item_id}")
    read = client.get(f"/api/v1/meals/{meal_id}")

    assert updated.status_code == 200
    assert updated.json()["food_name"] == "Brown rice"
    assert deleted.status_code == 204
    assert read.json()["items"] == []


def test_deleting_a_meal_cascades_to_its_items(client: TestClient, db_session) -> None:
    meal_id = client.post("/api/v1/meals", json=meal_payload()).json()["id"]
    client.post(f"/api/v1/meals/{meal_id}/items", json=item_payload())
    deleted = client.delete(f"/api/v1/meals/{meal_id}")

    assert deleted.status_code == 204
    assert client.get(f"/api/v1/meals/{meal_id}").status_code == 404
    assert db_session.scalars(select(MealItem)).all() == []


def test_meals_validate_values_timestamps_and_pagination(client: TestClient) -> None:
    future = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    invalid_meal = client.post("/api/v1/meals", json=meal_payload(meal_type="brunch"))
    invalid_timestamp = client.post("/api/v1/meals", json=meal_payload(eaten_at="2026-09-06T10:00:00"))
    future_timestamp = client.post("/api/v1/meals", json=meal_payload(eaten_at=future))
    meal_id = client.post("/api/v1/meals", json=meal_payload()).json()["id"]
    invalid_unit = client.post(f"/api/v1/meals/{meal_id}/items", json=item_payload(unit="cup"))
    invalid_quantity = client.post(f"/api/v1/meals/{meal_id}/items", json=item_payload(quantity=0))
    negative_nutrition = client.post(f"/api/v1/meals/{meal_id}/items", json={**item_payload(), "fat_g": -1})
    invalid_pagination = client.get("/api/v1/meals?limit=101")

    assert invalid_meal.status_code == 422
    assert invalid_timestamp.status_code == 422
    assert future_timestamp.status_code == 422
    assert invalid_unit.status_code == 422
    assert invalid_quantity.status_code == 422
    assert negative_nutrition.status_code == 422
    assert invalid_pagination.status_code == 422


def test_meals_and_items_do_not_expose_another_users_data(client: TestClient, db_session) -> None:
    local_meal = client.post("/api/v1/meals", json=meal_payload()).json()
    other_user = User(created_at=datetime(2100, 1, 1, tzinfo=timezone.utc), updated_at=datetime(2100, 1, 1, tzinfo=timezone.utc))
    db_session.add(other_user)
    db_session.flush()
    other_meal = Meal(user_id=other_user.id, meal_type=MealType.DINNER, eaten_at=datetime(2026, 9, 6, tzinfo=timezone.utc))
    db_session.add(other_meal)
    db_session.flush()
    other_item = MealItem(meal_id=other_meal.id, food_name="Other user's food", quantity=1, unit=FoodUnit.PIECE)
    db_session.add(other_item)
    db_session.commit()

    listed = client.get("/api/v1/meals")
    other_meal_response = client.get(f"/api/v1/meals/{other_meal.id}")
    other_item_response = client.patch(f"/api/v1/meals/{other_meal.id}/items/{other_item.id}", json={"food_name": "Changed"})

    assert listed.json()["total"] == 1
    assert listed.json()["items"][0]["id"] == local_meal["id"]
    assert other_meal_response.status_code == 404
    assert other_item_response.status_code == 404
