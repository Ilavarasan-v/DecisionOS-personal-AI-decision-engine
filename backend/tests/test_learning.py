"""
Tests for the learning service's feedback-driven weight adjustment.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

from backend.app.services.learning_service import (
    LEARNING_RATE,
    apply_feedback,
    calculate_new_weight,
    get_feedback_direction,
)


def test_learning_rate_is_a_small_positive_fraction():
    """
    Sanity check on the configured learning rate: it should nudge weights
    gently rather than causing large swings from a single feedback event.
    """
    assert 0 < LEARNING_RATE < 0.2


def test_positive_feedback_direction_logic():
    assert get_feedback_direction(5) == 1
    assert get_feedback_direction(4) == 1


def test_negative_feedback_direction_logic():
    assert get_feedback_direction(1) == -1
    assert get_feedback_direction(2) == -1


def test_neutral_feedback_direction_logic():
    assert get_feedback_direction(3) == 0


def test_positive_feedback_increases_weight():
    assert calculate_new_weight(0.80, 1) == 0.85


def test_negative_feedback_decreases_weight():
    assert calculate_new_weight(0.90, -1) == 0.85


def test_neutral_feedback_keeps_weight_unchanged():
    assert calculate_new_weight(0.70, 0) == 0.70


def test_weight_does_not_exceed_one():
    assert calculate_new_weight(0.99, 1) == 1.0


def test_weight_does_not_go_below_zero():
    assert calculate_new_weight(0.01, -1) == 0.0


def test_same_feedback_is_not_processed_twice():
    """
    The same feedback event must only be applied once.

    If PreferenceHistory already contains an entry with the feedback-specific
    source, apply_feedback() must return an empty list and must not modify
    preferences again.
    """
    feedback = SimpleNamespace(
        id="feedback-123",
        decision_id="decision-123",
        criterion_ratings={
            "price": 4,
            "performance": 2,
            "battery": 5,
        },
    )

    already_processed_history = SimpleNamespace(
        id="history-123",
        source="feedback:feedback-123",
    )

    db = MagicMock()

    (
        db.query.return_value
        .filter.return_value
        .first.return_value
    ) = already_processed_history

    result = apply_feedback(db=db, feedback=feedback)

    assert result == []


def test_new_feedback_updates_matching_preferences_and_creates_history():
    """
    A new feedback event should update only the preferences that have
    applicable criterion-level ratings and create PreferenceHistory records.
    """
    feedback = SimpleNamespace(
        id="feedback-new",
        decision_id="decision-new",
        criterion_ratings={
            "price": 4,
            "performance": 2,
            "battery": 3,
        },
    )

    decision = SimpleNamespace(
        id="decision-new",
        user_id="user-123",
    )

    price_preference = SimpleNamespace(
        criterion="price",
        weight=0.80,
    )

    performance_preference = SimpleNamespace(
        criterion="performance",
        weight=0.90,
    )

    battery_preference = SimpleNamespace(
        criterion="battery",
        weight=0.70,
    )

    db = MagicMock()

    # First query: check whether this feedback was already processed.
    processed_query = MagicMock()
    processed_query.filter.return_value.first.return_value = None

    # Second query: retrieve the decision.
    decision_query = MagicMock()
    decision_query.filter.return_value.first.return_value = decision

    # Third query: retrieve the user's preferences.
    preferences_query = MagicMock()
    preferences_query.filter.return_value.all.return_value = [
        price_preference,
        performance_preference,
        battery_preference,
    ]

    db.query.side_effect = [
        processed_query,
        decision_query,
        preferences_query,
    ]

    result = apply_feedback(db=db, feedback=feedback)

    # Only price and performance should change.
    # Battery has a neutral rating of 3.
    assert len(result) == 2

    assert price_preference.weight == 0.85
    assert performance_preference.weight == 0.85
    assert battery_preference.weight == 0.70

    assert result[0].criterion == "price"
    assert result[0].old_weight == 0.80
    assert result[0].new_weight == 0.85

    assert result[1].criterion == "performance"
    assert result[1].old_weight == 0.90
    assert result[1].new_weight == 0.85

    # Two changed preferences should produce two history records.
    assert db.add.call_count == 2

    # Changes should be committed once.
    db.commit.assert_called_once()