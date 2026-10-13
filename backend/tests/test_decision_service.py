from backend.app.services.decision_service import evaluate_option


def test_laptop_evaluation():

    laptop = {
        "price": 85000,
        "performance": 8.5,
        "battery": 9,
        "portability": 7,
    }

    preferences = {

        "price": {
            "weight": 0.85,
            "direction": "minimize",
            "min_value": 80000,
            "max_value": 100000,
        },

        "performance": {
            "weight": 0.95,
            "direction": "maximize",
            "min_value": 5,
            "max_value": 10,
        },

        "battery": {
            "weight": 0.80,
            "direction": "maximize",
            "min_value": 5,
            "max_value": 10,
        },

        "portability": {
            "weight": 0.65,
            "direction": "maximize",
            "min_value": 5,
            "max_value": 10,
        },
    }

    result = evaluate_option(
        option_attributes=laptop,
        preferences=preferences,
    )

    assert "final_score" in result
    assert "criteria" in result

    assert result["final_score"] > 0