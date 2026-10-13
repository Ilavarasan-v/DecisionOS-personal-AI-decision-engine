"""
Learning API routes for DecisionOS.

The learning endpoint takes previously submitted feedback
and applies it to the user's preference profile.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.models.feedback import Feedback
from backend.app.models.preference_history import PreferenceHistory
from backend.app.schemas.learning import (
    LearningResult,
    PreferenceHistoryRead,
    PreferenceLearningResult,
)
from backend.app.services.learning_service import apply_feedback


router = APIRouter()


@router.post(
    "/feedback/{feedback_id}",
    response_model=LearningResult,
)
def learn_from_feedback(
    feedback_id: str,
    db: Session = Depends(get_db),
):
    """
    Apply one feedback event to the user's preference profile.
    """

    # ---------------------------------------------------------
    # 1. Find feedback
    # ---------------------------------------------------------

    feedback = (
        db.query(Feedback)
        .filter(
            Feedback.id == feedback_id
        )
        .first()
    )

    if feedback is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found",
        )

    # ---------------------------------------------------------
    # 2. Apply learning
    # ---------------------------------------------------------

    history_entries = apply_feedback(
        db=db,
        feedback=feedback,
    )

    # ---------------------------------------------------------
    # 3. Build response
    # ---------------------------------------------------------

    updated_preferences = [
        PreferenceLearningResult(
            criterion=history.criterion,
            old_weight=history.old_weight,
            new_weight=history.new_weight,
            reason=history.reason,
        )
        for history in history_entries
    ]

    if not updated_preferences:

        message = (
            "No preference weights were updated. "
            "The feedback contained no applicable "
            "criterion-level learning signal."
        )

    else:

        message = (
            f"Updated {len(updated_preferences)} "
            f"preference(s) based on feedback."
        )

    return LearningResult(
        feedback_id=feedback.id,
        updated_preferences=updated_preferences,
        message=message,
    )


@router.get(
    "/history/user/{user_id}",
    response_model=List[PreferenceHistoryRead],
)
def get_user_learning_history(
    user_id: str,
    db: Session = Depends(get_db),
):
    """
    Retrieve the history of preference changes for a user.
    """

    history = (
        db.query(PreferenceHistory)
        .filter(
            PreferenceHistory.user_id == user_id
        )
        .order_by(
            PreferenceHistory.created_at.desc()
        )
        .all()
    )

    return history