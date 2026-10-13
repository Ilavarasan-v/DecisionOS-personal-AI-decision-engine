"""
SQLAlchemy ORM model for a candidate option within a decision
(e.g. one of several laptops being compared).
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from backend.app.database.connection import Base


class Option(Base):
    __tablename__ = "options"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    decision_id = Column(String, ForeignKey("decisions.id"), nullable=False, index=True)

    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    attributes = Column(Text, nullable=True)   # JSON-encoded key/value attributes
    score = Column(Float, nullable=True)         # computed by scoring_service

    created_at = Column(DateTime, default=datetime.utcnow)

    decision = relationship("Decision", back_populates="options")
