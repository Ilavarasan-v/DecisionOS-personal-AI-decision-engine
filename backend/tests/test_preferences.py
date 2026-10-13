"""
Unit tests for preference weight normalization.
"""

from backend.app.utils.normalization import normalize_weights


def test_normalize_weights_sums_to_one():
    raw = {"cost": 2.0, "quality": 2.0}
    normalized = normalize_weights(raw)

    assert normalized == {"cost": 0.5, "quality": 0.5}
    assert sum(normalized.values()) == 1.0


def test_normalize_weights_empty_input():
    assert normalize_weights({}) == {}


def test_normalize_weights_all_zero_falls_back_to_equal_share():
    raw = {"cost": 0.0, "quality": 0.0, "speed": 0.0}
    normalized = normalize_weights(raw)

    assert normalized == {"cost": 1 / 3, "quality": 1 / 3, "speed": 1 / 3}


def test_normalize_weights_single_category():
    assert normalize_weights({"cost": 5.0}) == {"cost": 1.0}
