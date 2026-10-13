from backend.app.services.tradeoff_service import analyze_option_tradeoffs


def test_analyze_option_tradeoffs_identifies_strengths_and_weaknesses():
    evaluated_option = {
        "criteria": {
            "price": {
                "normalized_score": 1.0,
            },
            "performance": {
                "normalized_score": 0.0,
            },
            "battery": {
                "normalized_score": 0.8,
            },
        }
    }

    result = analyze_option_tradeoffs(evaluated_option)

    assert result["strengths"] == ["price", "battery"]
    assert result["weaknesses"] == ["performance"]


def test_analyze_option_tradeoffs_handles_no_clear_strengths_or_weaknesses():
    evaluated_option = {
        "criteria": {
            "price": {
                "normalized_score": 0.5,
            },
            "performance": {
                "normalized_score": 0.6,
            },
        }
    }

    result = analyze_option_tradeoffs(evaluated_option)

    assert result["strengths"] == []
    assert result["weaknesses"] == []