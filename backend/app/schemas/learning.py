"""
Pydantic schemas for the DecisionOS learning engine.
"""

from datetime import datetime
from typing import List

from pydantic import BaseModel


class PreferenceLearningResult(BaseModel):
    """
    Represents one preference adjustment.
    """

    criterion: str

    old_weight: float

    new_weight: float

    reason: str


class LearningResult(BaseModel):
    """
    Result returned after applying feedback to the
    user's preference profile.
    """

    feedback_id: str

    updated_preferences: List[PreferenceLearningResult]

    message: str


class PreferenceHistoryRead(BaseModel):
    """
    Historical record of a preference change.
    """

    id: str

    user_id: str

    criterion: str

    old_weight: float

    new_weight: float

    reason: str

    source: str

    created_at: datetime