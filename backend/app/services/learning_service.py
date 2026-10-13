"""
Learning service for DecisionOS.

Criterion feedback represents how important a criterion should
be in the user's future decisions.

Importance scale:
    1-2: Decrease preference weight.
    3:   Leave preference weight unchanged.
    4-5: Increase preference weight.

Weights remain between 0.0 and 1.0.
Each feedback event is applied at most once when its changes
have already been recorded in preference history.
"""

from sqlalchemy.orm import Session

from backend.app.models.decision import Decision
from backend.app.models.feedback import Feedback
from backend.app.models.preference import Preference
from backend.app.models.preference_history import PreferenceHistory


# Maximum adjustment from one feedback event.
LEARNING_RATE = 0.05


IMPORTANCE_LABELS = {
    1: "not important",
    2: "slightly important",
    3: "moderately important",
    4: "very important",
    5: "extremely important",
}


def get_feedback_direction(rating: int) -> int:
    """
    Convert a criterion-importance rating into a direction.

    Ratings 1-2: decrease weight.
    Rating 3:    no change.
    Ratings 4-5: increase weight.
    """
    if rating >= 4:
        return 1

    if rating <= 2:
        return -1

    return 0


def calculate_new_weight(
    current_weight: float,
    direction: int,
) -> float:
    """
    Adjust a preference weight while keeping it between 0.0
    and 1.0.
    """
    new_weight = (
        current_weight + (direction * LEARNING_RATE)
    )

    return round(
        min(1.0, max(0.0, new_weight)),
        10,
    )


def apply_feedback(
    db: Session,
    feedback: Feedback,
) -> list[PreferenceHistory]:
    """
    Apply criterion-importance feedback to the user's profile.

    Returns the preference-history records created by this
    learning operation.
    """

    # 1. Avoid processing feedback that has already changed
    #    at least one preference weight.
    feedback_source = f"feedback:{feedback.id}"

    already_processed = (
        db.query(PreferenceHistory)
        .filter(
            PreferenceHistory.source == feedback_source
        )
        .first()
    )

    if already_processed is not None:
        return []

    # 2. Retrieve the associated decision.
    decision = (
        db.query(Decision)
        .filter(
            Decision.id == feedback.decision_id
        )
        .first()
    )

    if decision is None:
        return []

    # 3. Retrieve the user's existing preferences.
    preferences = (
        db.query(Preference)
        .filter(
            Preference.user_id == decision.user_id
        )
        .all()
    )

    if not preferences:
        return []

    # 4. Retrieve criterion-importance ratings.
    importance_ratings = feedback.criterion_ratings or {}

    if not importance_ratings:
        return []

    preferences_by_criterion = {
        preference.criterion: preference
        for preference in preferences
    }

    history_entries: list[PreferenceHistory] = []

    # 5. Update each matching preference independently.
    for criterion, rating in importance_ratings.items():

        preference = preferences_by_criterion.get(criterion)

        # Ignore criteria that do not exist in the profile.
        if preference is None:
            continue

        # Reject booleans, non-integers, and invalid ratings.
        if (
            isinstance(rating, bool)
            or not isinstance(rating, int)
            or rating < 1
            or rating > 5
        ):
            continue

        direction = get_feedback_direction(rating)

        # Rating 3 means moderate importance, so keep the weight.
        if direction == 0:
            continue

        old_weight = float(preference.weight)

        new_weight = calculate_new_weight(
            current_weight=old_weight,
            direction=direction,
        )

        # Do not record a change when the weight is already
        # at its applicable boundary.
        if new_weight == old_weight:
            continue

        # Update the stored preference used by future evaluations.
        preference.weight = new_weight

        importance_label = IMPORTANCE_LABELS[rating]

        if direction > 0:
            reason = (
                f"Preference weight increased because the user "
                f"marked '{criterion}' as {importance_label} "
                f"({rating}/5) for future decisions."
            )
        else:
            reason = (
                f"Preference weight decreased because the user "
                f"marked '{criterion}' as {importance_label} "
                f"({rating}/5) for future decisions."
            )

        history = PreferenceHistory(
            user_id=decision.user_id,
            criterion=criterion,
            old_weight=old_weight,
            new_weight=new_weight,
            reason=reason,
            source=feedback_source,
        )

        db.add(history)
        history_entries.append(history)

    # 6. Persist preference changes and learning history.
    if history_entries:
        db.commit()

        for history in history_entries:
            db.refresh(history)

    return history_entries