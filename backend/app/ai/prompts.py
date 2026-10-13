"""
Prompt templates used across the AI layer. Keeping them centralized makes
it easy to iterate on wording without hunting through service code.
"""

from typing import List, Optional


def build_explanation_prompt(
    decision_title: str,
    decision_description: Optional[str],
    ranked_options: List[dict],
) -> str:
    """
    Build a prompt asking the LLM to explain, in plain language, why the
    top-ranked option was recommended.

    `ranked_options` is a list of dicts: [{"name": ..., "score": ..., "rank": ...}, ...]
    """
    options_block = "\n".join(
        f"  {opt['rank']}. {opt['name']} — score: {opt['score']}" for opt in ranked_options
    )
    description_block = f"\nContext: {decision_description}" if decision_description else ""

    return (
        "You are the reasoning layer of a personal decision-assistant app. "
        "A user is deciding between several options, and each has been scored "
        "against their personal preferences.\n\n"
        f"Decision: {decision_title}{description_block}\n\n"
        f"Ranked options (highest score = best fit):\n{options_block}\n\n"
        "Write a short, friendly explanation (3-5 sentences) of why the "
        "top-ranked option is the best fit given the scores, and briefly "
        "mention one meaningful trade-off versus the runner-up. "
        "Do not invent details not present above."
    )


def build_preference_extraction_prompt(user_message: str) -> str:
    """
    Build a prompt asking the LLM to extract structured preference
    signals (category + weight) from a free-text user message.
    """
    return (
        "Extract decision-making preferences from the user's message below. "
        "Respond ONLY with a JSON array of objects with keys "
        "'category' (short snake_case label) and 'weight' (float 0.0-1.0 "
        "representing relative importance). If no preferences are present, "
        "return an empty array.\n\n"
        f"User message: \"{user_message}\""
    )
