from fastapi import APIRouter

from backend.app.api.routes import (
    analytics,
    decisions,
    feedback,
    learning,
    preferences,
    users,
)


api_router = APIRouter()


api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"],
)

api_router.include_router(
    preferences.router,
    prefix="/preferences",
    tags=["preferences"],
)

api_router.include_router(
    decisions.router,
    prefix="/decisions",
    tags=["decisions"],
)

api_router.include_router(
    feedback.router,
    prefix="/feedback",
    tags=["feedback"],
)

api_router.include_router(
    learning.router,
    prefix="/learning",
    tags=["learning"],
)

api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["analytics"],
)