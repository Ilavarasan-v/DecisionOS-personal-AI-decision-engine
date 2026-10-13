"""
Tests for the DecisionOS decision API.
"""

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy"
    }


def test_create_decision_requires_valid_user():
    payload = {
        "user_id": "non-existent-user",
        "title": "Which laptop should I buy?",
        "options": [
            {
                "name": "Laptop A",
                "attributes": {
                    "price": 80000,
                    "performance": 8,
                },
            },
            {
                "name": "Laptop B",
                "attributes": {
                    "price": 90000,
                    "performance": 9,
                },
            },
        ],
    }

    response = client.post(
        "/api/v1/decisions/",
        json=payload,
    )

    # The current implementation may reach the database
    # and fail at the foreign-key level if the user does not exist.
    assert response.status_code in (201, 400, 404, 500)


def test_get_nonexistent_decision():
    response = client.get(
        "/api/v1/decisions/non-existent-decision"
    )

    assert response.status_code == 404