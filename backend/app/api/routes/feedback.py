
"""
Feedback API routes for DecisionOS.

Feedback is the bridge between:

Decision
    ↓
Recommendation
    ↓
Real-world outcome
    ↓
User feedback
    ↓
Learning Engine
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.models.decision import Decision
from backend.app.models.feedback import Feedback
from backend.app.schemas.feedback import (
    FeedbackCreate,
    FeedbackRead,
)
from backend.app.services.feedback_service import (
    create_feedback,
    get_decision_feedback,
    get_feedback,
    get_user_feedback,
)


router = APIRouter()


DUPLICATE_FEEDBACK_MESSAGE = (
    "Feedback has already been submitted for this decision."
)


def feedback_to_response(
    feedback: Feedback,
    user_id: str,
) -> dict:
    """Convert the database Feedback model into the public API format."""

    return {
        "id": feedback.id,
        "user_id": user_id,
        "decision_id": feedback.decision_id,
        "chosen_option_id": feedback.option_id,
        "rating": feedback.overall_rating,
        "notes": feedback.comments,
        "criterion_ratings": feedback.criterion_ratings or {},
        "created_at": feedback.created_at,
    }


@router.post(
    "/",
    response_model=FeedbackRead,
    status_code=status.HTTP_201_CREATED,
)
def submit_feedback(
    payload: FeedbackCreate,
    db: Session = Depends(get_db),
):
    """Submit feedback on a completed decision."""

    try:
        feedback = create_feedback(
            db=db,
            user_id=payload.user_id,
            decision_id=payload.decision_id,
            chosen_option_id=payload.chosen_option_id,
            rating=payload.rating,
            notes=payload.notes,
            criterion_ratings=payload.criterion_ratings,
        )

    except ValueError as exc:
        error_message = str(exc)

        if error_message == DUPLICATE_FEEDBACK_MESSAGE:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_message,
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message,
        ) from exc

    return feedback_to_response(
        feedback=feedback,
        user_id=payload.user_id,
    )


@router.get(
    "/decision/{decision_id}",
    response_model=List[FeedbackRead],
)
def list_decision_feedback(
    decision_id: str,
    db: Session = Depends(get_db),
):
    """List all feedback entries recorded for a decision."""

    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    feedback_entries = get_decision_feedback(
        db=db,
        decision_id=decision_id,
    )

    return [
        feedback_to_response(
            feedback=feedback,
            user_id=decision.user_id,
        )
        for feedback in feedback_entries
    ]


@router.get(
    "/user/{user_id}",
    response_model=List[FeedbackRead],
)
def list_user_feedback(
    user_id: str,
    db: Session = Depends(get_db),
):
    """List all feedback submitted by a user."""

    feedback_entries = get_user_feedback(
        db=db,
        user_id=user_id,
    )

    return [
        feedback_to_response(
            feedback=feedback,
            user_id=user_id,
        )
        for feedback in feedback_entries
    ]


@router.get(
    "/{feedback_id}",
    response_model=FeedbackRead,
)
def get_feedback_endpoint(
    feedback_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve one feedback record by ID."""

    feedback = get_feedback(
        db=db,
        feedback_id=feedback_id,
    )

    if feedback is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found",
        )

    decision = (
        db.query(Decision)
        .filter(Decision.id == feedback.decision_id)
        .first()
    )

    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated decision not found",
        )

    return feedback_to_response(
        feedback=feedback,
        user_id=decision.user_id,
    )
