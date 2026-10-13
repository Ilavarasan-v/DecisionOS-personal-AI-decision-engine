from typing import Any


def analyze_option_tradeoffs(
    evaluated_option: dict[str, Any],
) -> dict[str, Any]:
    criteria = evaluated_option.get("criteria", {})

    strengths = []
    weaknesses = []

    for criterion, result in criteria.items():
        normalized_score = result["normalized_score"]

        if normalized_score >= 0.75:
            strengths.append(criterion)
        elif normalized_score <= 0.25:
            weaknesses.append(criterion)

    return {
        "strengths": strengths,
        "weaknesses": weaknesses,
    }