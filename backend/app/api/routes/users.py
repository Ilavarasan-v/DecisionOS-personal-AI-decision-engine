"""
User account endpoints: create, fetch, update, delete.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.schemas.user import UserCreate, UserRead, UserUpdate
from backend.app.services.user_service import (
    create_user,
    delete_user,
    get_user,
    update_user,
)


router = APIRouter()


@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def create_user_endpoint(
    payload: UserCreate,
    db: Session = Depends(get_db),
):
    """Create a new user account."""

    return create_user(db, payload)


@router.get(
    "/{user_id}",
    response_model=UserRead,
)
def get_user_endpoint(
    user_id: str,
    db: Session = Depends(get_db),
):
    """Fetch a single user by id."""

    user = get_user(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.patch(
    "/{user_id}",
    response_model=UserRead,
)
def update_user_endpoint(
    user_id: str,
    payload: UserUpdate,
    db: Session = Depends(get_db),
):
    """Update a user's profile fields."""

    user = get_user(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return update_user(db, user, payload)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user_endpoint(
    user_id: str,
    db: Session = Depends(get_db),
):
    """Delete a user account."""

    user = get_user(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    delete_user(db, user)