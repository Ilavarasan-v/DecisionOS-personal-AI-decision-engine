from typing import Any


def satisfies_constraint(
    value: float,
    constraint_type: str,
    constraint_value: float,
) -> bool:
    """
    Check whether a value satisfies a hard constraint.
    """

    if constraint_type == "maximum":
        return value <= constraint_value

    if constraint_type == "minimum":
        return value >= constraint_value

    if constraint_type == "equal":
        return value == constraint_value

    raise ValueError(
        f"Invalid constraint type: {constraint_type}"
    )