from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.schemas.user import UserCreate, UserUpdate


def create_user(
    db: Session,
    user_data: UserCreate,
) -> User:
    user = User(
        name=user_data.name,
        email=user_data.email,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_user(
    db: Session,
    user_id: str,
) -> User | None:
    return (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )


def update_user(
    db: Session,
    user: User,
    user_data: UserUpdate,
) -> User:
    update_data = user_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user


def delete_user(
    db: Session,
    user: User,
) -> None:
    db.delete(user)
    db.commit()