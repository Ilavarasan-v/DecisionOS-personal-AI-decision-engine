"""
Feedback service for DecisionOS.

Responsibilities:
- Validate feedback relationships
- Prevent duplicate feedback for a decision
- Create feedback records
- Retrieve feedback by ID
- Retrieve feedback for a decision
- Retrieve feedback belonging to a user
"""

from typing import List

from sqlalchemy.orm import Session

from backend.app.models.decision import Decision
from backend.app.models.decision_option import DecisionOption
from backend.app.models.feedback import Feedback


def create_feedback(
    db: Session,
    user_id: str,
    decision_id: str,
    chosen_option_id: str,
    rating: int,
    notes: str | None = None,
    criterion_ratings: dict | None = None,
) -> Feedback:
    """
    Create feedback for a completed decision.

    A user may submit feedback only once per decision.

    Validates:
    1. Satisfaction rating is between 1 and 5.
    2. Decision exists.
    3. User owns the decision.
    4. Feedback does not already exist for the decision.
    5. Selected option exists.
    6. Selected option belongs to the decision.
    """

    # 1. Validate overall satisfaction rating.
    if (
        isinstance(rating, bool)
        or not isinstance(rating, int)
        or rating < 1
        or rating > 5
    ):
        raise ValueError("Rating must be between 1 and 5")

    # 2. Find the decision.
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if decision is None:
        raise ValueError("Decision not found")

    # 3. Verify decision ownership.
    if decision.user_id != user_id:
        raise ValueError("User does not own this decision")

    # 4. Prevent duplicate feedback.
    existing_feedback = (
        db.query(Feedback)
        .filter(Feedback.decision_id == decision_id)
        .first()
    )

    if existing_feedback is not None:
        raise ValueError(
            "Feedback has already been submitted for this decision."
        )

    # 5. Find the selected option.
    option = (
        db.query(DecisionOption)
        .filter(DecisionOption.id == chosen_option_id)
        .first()
    )

    if option is None:
        raise ValueError("Selected option not found")

    # 6. Verify the option belongs to this decision.
    if option.decision_id != decision_id:
        raise ValueError(
            "Selected option does not belong to this decision"
        )

    # 7. Create and save feedback.
    feedback = Feedback(
        decision_id=decision_id,
        option_id=chosen_option_id,
        overall_rating=rating,
        criterion_ratings=criterion_ratings or {},
        comments=notes,
    )

    try:
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
    except Exception:
        db.rollback()
        raise

    return feedback


def get_feedback(
    db: Session,
    feedback_id: str,
) -> Feedback | None:
    """Retrieve feedback by its ID."""

    return (
        db.query(Feedback)
        .filter(Feedback.id == feedback_id)
        .first()
    )


def get_decision_feedback(
    db: Session,
    decision_id: str,
) -> List[Feedback]:
    """Retrieve feedback records for a decision."""

    return (
        db.query(Feedback)
        .filter(Feedback.decision_id == decision_id)
        .order_by(Feedback.created_at.desc())
        .all()
    )


def get_user_feedback(
    db: Session,
    user_id: str,
) -> List[Feedback]:
    """Retrieve feedback belonging to a user's decisions."""

    return (
        db.query(Feedback)
        .join(
            Decision,
            Feedback.decision_id == Decision.id,
        )
        .filter(Decision.user_id == user_id)
        .order_by(Feedback.created_at.desc())
        .all()
    )