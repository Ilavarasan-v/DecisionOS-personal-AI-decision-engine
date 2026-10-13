from sqlalchemy.orm import Session

from backend.app.models.preference import Preference
from backend.app.schemas.preference import PreferenceCreate, PreferenceUpdate


def create_preference(
    db: Session,
    preference_data: PreferenceCreate,
) -> Preference:
    preference = Preference(
        user_id=preference_data.user_id,
        criterion=preference_data.criterion,
        weight=preference_data.weight,
        direction=preference_data.direction,
        source=preference_data.source,
        confidence=preference_data.confidence,
    )

    db.add(preference)
    db.commit()
    db.refresh(preference)

    return preference


def get_preference(
    db: Session,
    preference_id: str,
) -> Preference | None:
    return (
        db.query(Preference)
        .filter(Preference.id == preference_id)
        .first()
    )


def get_user_preferences(
    db: Session,
    user_id: str,
) -> list[Preference]:
    return (
        db.query(Preference)
        .filter(Preference.user_id == user_id)
        .all()
    )


def update_preference(
    db: Session,
    preference: Preference,
    preference_data: PreferenceUpdate,
) -> Preference:
    update_data = preference_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(preference, field, value)

    db.commit()
    db.refresh(preference)

    return preference


def delete_preference(
    db: Session,
    preference: Preference,
) -> None:
    db.delete(preference)
    db.commit()