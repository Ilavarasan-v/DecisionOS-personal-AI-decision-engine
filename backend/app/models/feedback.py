
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database.connection import Base


class Feedback(Base):
    __tablename__ = "feedback"

    __table_args__ = (
        UniqueConstraint(
            "decision_id",
            name="uq_feedback_decision_id",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    decision_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("decisions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    option_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("decision_options.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    overall_rating: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    criterion_ratings: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    comments: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
