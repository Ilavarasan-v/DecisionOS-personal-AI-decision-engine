"""
Aggregate insight endpoints: decision history trends, preference drift
over time, and summary statistics for the insights dashboard.
"""

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/user/{user_id}/summary")
def get_user_summary(user_id: str):
    """Return high-level stats: total decisions, avg satisfaction, top preferences."""
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/user/{user_id}/preference-trends")
def get_preference_trends(user_id: str):
    """Return how a user's preference weights have shifted over time."""
    raise HTTPException(status_code=501, detail="Not implemented yet")
