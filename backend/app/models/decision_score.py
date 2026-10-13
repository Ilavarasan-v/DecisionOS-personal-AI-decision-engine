from uuid import uuid4

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database.connection import Base


class DecisionScore(Base):
    __tablename__ = "decision_scores"

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

    criterion: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    raw_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    normalized_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    preference_weight: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    weighted_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )