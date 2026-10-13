"""
Generates a natural-language explanation for why the decision engine
recommended a particular option, using the configured LLM provider.
"""

from typing import List

from backend.app.ai.llm_service import LLMService
from backend.app.ai.prompts import build_explanation_prompt
from backend.app.models.decision import Decision
from backend.app.schemas.decision import RankedOption

llm_service = LLMService()


def generate_explanation(decision: Decision, ranked_options: List[RankedOption]) -> str:
    """
    Build a prompt from the decision + ranked options and ask the LLM
    to explain the recommendation in plain language.
    """
    if not ranked_options:
        return "No options were available to evaluate."

    prompt = build_explanation_prompt(
        decision_title=decision.title,
        decision_description=decision.description,
        ranked_options=[
            {"name": ro.option.name, "score": ro.score, "rank": ro.rank}
            for ro in ranked_options
        ],
    )

    try:
        return llm_service.complete(prompt)
    except Exception:
        # Fall back to a deterministic explanation if the LLM call fails,
        # so the API never breaks purely because of an upstream provider issue.
        top = ranked_options[0]
        return (
            f"Based on your preferences, '{top.option.name}' scored highest "
            f"({top.score}) among the {len(ranked_options)} options considered."
        )
