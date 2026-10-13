
"""
DecisionOS decision API routes.

Endpoints:
- Create a decision
- Retrieve a decision
- Evaluate a decision
- List a user's decisions
"""

from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.ai.reasoning_service import generate_decision_explanation
from backend.app.database.connection import get_db
from backend.app.models.decision_option import DecisionOption
from backend.app.models.decision_score import DecisionScore
from backend.app.schemas.decision import (
    DecisionCreate,
    DecisionRead,
    DecisionResult,
    OptionRead,
    RankedOption,
)
from backend.app.services.decision_service import (
    create_decision,
    evaluate_decision_options,
    get_decision,
    get_decision_options,
    get_user_decisions,
    get_user_preferences_for_decision,
)

router = APIRouter()


def option_to_schema(
    option: DecisionOption,
    score: float | None = None,
) -> OptionRead:
    """Convert a database option into an API response schema."""
    return OptionRead(
        id=option.id,
        name=option.name,
        description=option.description,
        attributes=option.attributes,
        score=score,
    )


def get_persisted_option_scores(
    db: Session,
    decision_id: str,
) -> dict[str, float]:
    """
    Calculate each option's overall score from its persisted
    criterion-level weighted scores and preference weights.
    """
    score_rows = (
        db.query(DecisionScore)
        .filter(DecisionScore.decision_id == decision_id)
        .all()
    )

    totals: dict[str, dict[str, float]] = {}

    for row in score_rows:
        option_totals = totals.setdefault(
            row.option_id,
            {"weighted_score": 0.0, "weight": 0.0},
        )

        option_totals["weighted_score"] += row.weighted_score
        option_totals["weight"] += row.preference_weight

    return {
        option_id: (
            round(values["weighted_score"] / values["weight"], 10)
            if values["weight"] > 0
            else 0.0
        )
        for option_id, values in totals.items()
    }


def decision_to_response(
    decision,
    options,
    db: Session,
) -> dict:
    """Build a decision response with persisted option scores."""
    option_scores = get_persisted_option_scores(
        db=db,
        decision_id=decision.id,
    )

    return {
        "id": decision.id,
        "user_id": decision.user_id,
        "title": decision.title,
        "description": decision.description,
        "status": decision.status,
        "chosen_option_id": decision.chosen_option_id,
        "explanation": decision.explanation,
        "options": [
            option_to_schema(
                option=option,
                score=option_scores.get(option.id),
            )
            for option in options
        ],
        "created_at": decision.created_at,
        "updated_at": decision.updated_at,
    }


@router.post(
    "/",
    response_model=DecisionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_decision_endpoint(
    payload: DecisionCreate,
    db: Session = Depends(get_db),
):
    """Create a decision with candidate options."""
    try:
        decision = create_decision(
            db=db,
            user_id=payload.user_id,
            title=payload.title,
            description=payload.description,
            options=payload.options,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    options = get_decision_options(
        db=db,
        decision_id=decision.id,
    )

    return decision_to_response(
        decision=decision,
        options=options,
        db=db,
    )


# This static route must appear before /{decision_id}.
@router.get(
    "/user/{user_id}",
    response_model=List[DecisionRead],
)
def list_user_decisions(
    user_id: str,
    db: Session = Depends(get_db),
):
    """Return all decisions belonging to a user."""
    decisions = get_user_decisions(
        db=db,
        user_id=user_id,
    )

    results = []

    for decision in decisions:
        options = get_decision_options(
            db=db,
            decision_id=decision.id,
        )

        results.append(
            decision_to_response(
                decision=decision,
                options=options,
                db=db,
            )
        )

    return results


@router.get(
    "/{decision_id}",
    response_model=DecisionRead,
)
def get_decision_endpoint(
    decision_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve a decision by ID."""
    decision = get_decision(
        db=db,
        decision_id=decision_id,
    )

    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    options = get_decision_options(
        db=db,
        decision_id=decision.id,
    )

    return decision_to_response(
        decision=decision,
        options=options,
        db=db,
    )


@router.post(
    "/{decision_id}/evaluate",
    response_model=DecisionResult,
)
def evaluate_decision(
    decision_id: str,
    db: Session = Depends(get_db),
):
    """
    Evaluate options deterministically, generate an AI explanation,
    persist criterion-level scores, and return the ranking.
    """
    # 1. Retrieve decision.
    decision = get_decision(
        db=db,
        decision_id=decision_id,
    )

    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    # 2. Retrieve candidate options.
    options = get_decision_options(
        db=db,
        decision_id=decision.id,
    )

    if not options:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Decision has no candidate options",
        )

    # 3. Retrieve user preferences.
    preferences = get_user_preferences_for_decision(
        db=db,
        user_id=decision.user_id,
    )

    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no stored preferences",
        )

    # 4. Evaluate and rank options.
    ranked_results = evaluate_decision_options(
        preferences=preferences,
        options=options,
    )

    if not ranked_results:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "No options could be evaluated "
                "against the user's preferences"
            ),
        )

    # 5. Build option lookup.
    option_by_id = {
        option.id: option
        for option in options
    }

    ranked_options: list[RankedOption] = []

    for result in ranked_results:
        option = option_by_id[result["id"]]

        ranked_options.append(
            RankedOption(
                option=option_to_schema(
                    option=option,
                    score=result["final_score"],
                ),
                rank=result["rank"],
                score=result["final_score"],
                reasoning=None,
                tradeoffs=result["tradeoffs"],
            )
        )

    # 6. Select top-ranked recommendation.
    recommendation = ranked_options[0].option

    # 7. Build recommendation context.
    recommendation_context = {
        "name": recommendation.name,
        "score": ranked_options[0].score,
    }

    # 8. Build ranked-options context.
    ranked_context = [
        {
            "name": ranked_option.option.name,
            "score": ranked_option.score,
            "rank": ranked_option.rank,
            "tradeoffs": {
                "strengths": ranked_option.tradeoffs.strengths,
                "weaknesses": ranked_option.tradeoffs.weaknesses,
            },
        }
        for ranked_option in ranked_options
    ]

    # 9. Build preference context.
    preference_context = [
        {
            "criterion": preference.criterion,
            "weight": preference.weight,
            "direction": preference.direction,
        }
        for preference in preferences
    ]

    # 10. Generate explanation before persisting the evaluation.
    try:
        explanation = generate_decision_explanation(
            recommendation=recommendation_context,
            ranked_options=ranked_context,
            preferences=preference_context,
        )
    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI explanation generation failed: {exc}",
        ) from exc

    # 11. Persist score records and the completed decision together.
    try:
        # Replace prior score records if this decision is evaluated again.
        (
            db.query(DecisionScore)
            .filter(DecisionScore.decision_id == decision.id)
            .delete(synchronize_session=False)
        )

        for result in ranked_results:
            option_id = result["id"]

            for criterion, criterion_result in result["criteria"].items():
                db.add(
                    DecisionScore(
                        decision_id=decision.id,
                        option_id=option_id,
                        criterion=criterion,
                        raw_value=float(criterion_result["value"]),
                        normalized_value=float(
                            criterion_result["normalized_score"]
                        ),
                        preference_weight=float(
                            criterion_result["weight"]
                        ),
                        weighted_score=float(
                            criterion_result["weighted_score"]
                        ),
                    )
                )

        now = datetime.now(timezone.utc)

        decision.chosen_option_id = recommendation.id
        decision.explanation = explanation
        decision.status = "completed"
        decision.completed_at = now
        decision.updated_at = now

        db.commit()
        db.refresh(decision)

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to persist decision evaluation results",
        ) from exc

    # 12. Return the evaluation result.
    return DecisionResult(
        decision_id=decision.id,
        ranked_options=ranked_options,
        recommendation=recommendation,
        explanation=explanation,
    )
