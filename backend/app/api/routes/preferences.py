from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.schemas.preference import (
    PreferenceCreate,
    PreferenceRead,
    PreferenceUpdate,
)
from backend.app.services.preference_service import (
    create_preference,
    delete_preference,
    get_preference,
    get_user_preferences,
    update_preference,
)


router = APIRouter()


@router.post(
    "",
    response_model=PreferenceRead,
    status_code=status.HTTP_201_CREATED,
)
def create(
    preference_data: PreferenceCreate,
    db: Session = Depends(get_db),
):
    return create_preference(db, preference_data)


@router.get(
    "/{preference_id}",
    response_model=PreferenceRead,
)
def get(
    preference_id: str,
    db: Session = Depends(get_db),
):
    preference = get_preference(db, preference_id)

    if preference is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preference not found",
        )

    return preference


@router.get(
    "/user/{user_id}",
    response_model=list[PreferenceRead],
)
def get_for_user(
    user_id: str,
    db: Session = Depends(get_db),
):
    return get_user_preferences(db, user_id)


@router.put(
    "/{preference_id}",
    response_model=PreferenceRead,
)
def update(
    preference_id: str,
    preference_data: PreferenceUpdate,
    db: Session = Depends(get_db),
):
    preference = get_preference(db, preference_id)

    if preference is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preference not found",
        )

    return update_preference(
        db,
        preference,
        preference_data,
    )


@router.delete(
    "/{preference_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete(
    preference_id: str,
    db: Session = Depends(get_db),
):
    preference = get_preference(db, preference_id)

    if preference is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preference not found",
        )

    delete_preference(db, preference)