from backend.app.services.ranking_service import rank_options


def test_rank_options():
    preferences = {
        "price": {
            "weight": 0.8,
            "direction": "minimize",
            "min_value": 20_000,
            "max_value": 50_000,
        },
        "performance": {
            "weight": 0.9,
            "direction": "maximize",
            "min_value": 5,
            "max_value": 10,
        },
        "battery": {
            "weight": 0.7,
            "direction": "maximize",
            "min_value": 5,
            "max_value": 10,
        },
    }

    options = [
        {
            "name": "Phone A",
            "price": 30_000,
            "performance": 8,
            "battery": 8,
        },
        {
            "name": "Phone B",
            "price": 40_000,
            "performance": 10,
            "battery": 9,
        },
        {
            "name": "Phone C",
            "price": 25_000,
            "performance": 7,
            "battery": 7,
        },
    ]

    result = rank_options(
        options=options,
        preferences=preferences,
    )

    assert len(result) == 3

    assert result[0]["rank"] == 1
    assert result[1]["rank"] == 2
    assert result[2]["rank"] == 3

    # Scores must be ordered from highest to lowest.
    assert (
        result[0]["final_score"]
        >= result[1]["final_score"]
        >= result[2]["final_score"]
    )


def test_rank_options_preserves_criteria():
    preferences = {
        "price": {
            "weight": 1.0,
            "direction": "minimize",
            "min_value": 20_000,
            "max_value": 50_000,
        }
    }

    options = [
        {
            "name": "Phone A",
            "price": 30_000,
        }
    ]

    result = rank_options(
        options=options,
        preferences=preferences,
    )

    assert "criteria" in result[0]
    assert "price" in result[0]["criteria"]


def test_rank_options_empty_list():
    preferences = {
        "price": {
            "weight": 1.0,
            "direction": "minimize",
            "min_value": 20_000,
            "max_value": 50_000,
        }
    }

    result = rank_options(
        options=[],
        preferences=preferences,
    )

    assert result == []