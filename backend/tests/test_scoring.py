from backend.app.services.scoring_service import (
    calculate_final_score,
    calculate_weighted_score,
    normalize_value,
)


def test_normalize_maximize():
    score = normalize_value(
        value=80,
        minimum=60,
        maximum=100,
        direction="maximize",
    )

    assert score == 0.5


def test_normalize_minimize():
    score = normalize_value(
        value=30_000,
        minimum=20_000,
        maximum=40_000,
        direction="minimize",
    )

    assert score == 0.5


def test_normalize_same_values():
    score = normalize_value(
        value=80,
        minimum=80,
        maximum=80,
        direction="maximize",
    )

    assert score == 1.0


def test_weighted_score():
    score = calculate_weighted_score(
        normalized_value=0.8,
        weight=0.9,
    )

    assert score == 0.72


def test_final_score():
    score = calculate_final_score(
        weighted_scores=[0.72, 0.56],
        weights=[0.9, 0.7],
    )

    assert score == 0.8


def test_final_score_without_weights():
    score = calculate_final_score(
        weighted_scores=[],
        weights=[],
    )

    assert score == 0.0