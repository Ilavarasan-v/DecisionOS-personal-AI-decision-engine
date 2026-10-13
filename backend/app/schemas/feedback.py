"""
Pydantic schemas for DecisionOS feedback.

The public API uses user-friendly names:

- chosen_option_id
- rating
- notes

The database model internally uses:

- option_id
- overall_rating
- comments

Criterion ratings represent how important each criterion
is to the user's future decisions.
"""

from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class FeedbackCreate(BaseModel):
    """
    Payload submitted after a user evaluates the outcome
    of a previous decision.

    Overall satisfaction measures the user's satisfaction
    with the decision outcome.

    Criterion ratings indicate how important each criterion
    should be in future decisions.
    """

    user_id: str = Field(
        ...,
        min_length=1,
        description="Identifier of the user submitting feedback.",
    )

    decision_id: str = Field(
        ...,
        min_length=1,
        description="Identifier of the evaluated decision.",
    )

    chosen_option_id: str = Field(
        ...,
        min_length=1,
        description="Identifier of the option the user actually chose.",
    )

    rating: int = Field(
        ...,
        ge=1,
        le=5,
        description=(
            "Overall satisfaction score from 1 to 5, "
            "where 1 means very dissatisfied and 5 means "
            "very satisfied."
        ),
    )

    notes: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Optional comments about the decision outcome.",
    )

    criterion_ratings: Dict[str, int] = Field(
        default_factory=dict,
        description=(
            "Optional criterion-importance ratings from 1 to 5. "
            "Ratings 1-2 decrease the corresponding preference "
            "weight, rating 3 leaves it unchanged, and ratings "
            "4-5 increase it. These ratings help personalize "
            "future decision recommendations."
        ),
    )


class FeedbackRead(BaseModel):
    """
    Feedback returned by the API.

    Criterion ratings represent the importance assigned to
    each criterion for future decisions.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str

    user_id: str

    decision_id: str

    chosen_option_id: str

    rating: int = Field(
        description="Overall satisfaction score from 1 to 5.",
    )

    notes: Optional[str] = None

    criterion_ratings: Dict[str, int] = Field(
        default_factory=dict,
        description=(
            "Criterion-importance ratings from 1 to 5, "
            "used to guide future preference-weight updates."
        ),
    )

    created_at: datetime