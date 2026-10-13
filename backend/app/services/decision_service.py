"""
Decision evaluation service for DecisionOS.

Responsibilities:
- Evaluate a single option against preferences
- Build preference configuration from candidate options
- Evaluate and rank multiple options
- Analyze option strengths and weaknesses
- Validate users
- Create and retrieve decisions
"""

from typing import Dict, List

from sqlalchemy.orm import Session

from backend.app.models.decision import Decision
from backend.app.models.decision_option import DecisionOption
from backend.app.models.preference import Preference
from backend.app.models.user import User
from backend.app.services.scoring_service import (
    calculate_final_score,
    calculate_weighted_score,
    normalize_value,
)
from backend.app.services.tradeoff_service import analyze_option_tradeoffs


Direction = str


def evaluate_option(
    option_attributes: Dict[str, float],
    preferences: Dict[str, dict],
) -> dict:
    """
    Evaluate one option against a configured preference set.

    Each criterion is:
    1. Normalized to a 0-1 score.
    2. Multiplied by its preference weight.
    3. Included in the final weighted score.
    """

    weighted_scores: list[float] = []
    preference_weights: list[float] = []
    criterion_results: dict = {}

    for criterion, preference in preferences.items():

        # Ignore criteria that are not available for this option.
        if criterion not in option_attributes:
            continue

        value = option_attributes[criterion]

        weight = preference["weight"]
        direction = preference["direction"]

        min_value = preference["min_value"]
        max_value = preference["max_value"]

        normalized = normalize_value(
            value=value,
            minimum=min_value,
            maximum=max_value,
            direction=direction,
        )

        weighted = calculate_weighted_score(
            normalized_value=normalized,
            weight=weight,
        )

        weighted_scores.append(weighted)
        preference_weights.append(weight)

        criterion_results[criterion] = {
            "value": value,
            "weight": weight,
            "direction": direction,
            "normalized_score": normalized,
            "weighted_score": weighted,
        }

    final_score = calculate_final_score(
        weighted_scores=weighted_scores,
        weights=preference_weights,
    )

    return {
        "final_score": final_score,
        "criteria": criterion_results,
    }


def build_preference_config(
    preferences: List[Preference],
    options: List[DecisionOption],
) -> Dict[str, dict]:
    """
    Convert database preferences into the configuration required
    by the scoring engine.

    Minimum and maximum values are calculated from the candidate
    options for each criterion.
    """

    config: Dict[str, dict] = {}

    for preference in preferences:

        values: list[float] = []

        for option in options:

            if not option.attributes:
                continue

            value = option.attributes.get(preference.criterion)

            if isinstance(value, (int, float)):
                values.append(float(value))

        # If no candidate contains this criterion, skip it.
        if not values:
            continue

        config[preference.criterion] = {
            "weight": preference.weight,
            "direction": preference.direction,
            "min_value": min(values),
            "max_value": max(values),
        }

    return config


def evaluate_decision_options(
    preferences: List[Preference],
    options: List[DecisionOption],
) -> list[dict]:
    """
    Evaluate all candidate options and return them ranked
    from highest score to lowest score.

    Each evaluated option also includes trade-off information:
    - strengths
    - weaknesses
    """

    preference_config = build_preference_config(
        preferences=preferences,
        options=options,
    )

    evaluated_options: list[dict] = []

    for option in options:

        attributes = {}

        if option.attributes:
            attributes = {
                key: value
                for key, value in option.attributes.items()
                if isinstance(value, (int, float))
            }

        evaluation = evaluate_option(
            option_attributes=attributes,
            preferences=preference_config,
        )

        evaluated_option = {
            "id": option.id,
            "name": option.name,
            "final_score": evaluation["final_score"],
            "criteria": evaluation["criteria"],
        }

        # Analyze the option's strengths and weaknesses
        # using its criterion-level normalized scores.
        tradeoffs = analyze_option_tradeoffs(
            evaluated_option=evaluated_option,
        )

        evaluated_option["tradeoffs"] = tradeoffs

        evaluated_options.append(evaluated_option)

    # Highest score gets rank 1.
    evaluated_options.sort(
        key=lambda item: item["final_score"],
        reverse=True,
    )

    for position, result in enumerate(evaluated_options, start=1):
        result["rank"] = position

    return evaluated_options


def get_user_preferences_for_decision(
    db: Session,
    user_id: str,
) -> List[Preference]:
    """
    Retrieve all preferences belonging to a user.
    """

    return (
        db.query(Preference)
        .filter(Preference.user_id == user_id)
        .all()
    )


def create_decision(
    db: Session,
    user_id: str,
    title: str,
    description: str | None,
    options: list,
) -> Decision:
    """
    Create a decision and its candidate options.

    The user must exist before the decision can be created.
    """

    # Validate the user before inserting the decision.
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        raise ValueError("User not found")

    decision = Decision(
        user_id=user_id,
        title=title,
        category="general",
        description=description,
        status="draft",
    )

    db.add(decision)

    # Generate the decision ID before creating child options.
    db.flush()

    for option_data in options:

        option = DecisionOption(
            decision_id=decision.id,
            name=option_data.name,
            description=option_data.description,
            attributes=option_data.attributes or {},
        )

        db.add(option)

    db.commit()
    db.refresh(decision)

    return decision


def get_decision(
    db: Session,
    decision_id: str,
) -> Decision | None:
    """
    Retrieve a decision by ID.
    """

    return (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )


def get_decision_options(
    db: Session,
    decision_id: str,
) -> List[DecisionOption]:
    """
    Retrieve all options belonging to a decision.
    """

    return (
        db.query(DecisionOption)
        .filter(DecisionOption.decision_id == decision_id)
        .all()
    )


def get_user_decisions(
    db: Session,
    user_id: str,
) -> List[Decision]:
    """
    Retrieve all decisions created by a user,
    newest first.
    """

    return (
        db.query(Decision)
        .filter(Decision.user_id == user_id)
        .order_by(Decision.created_at.desc())
        .all()
    )