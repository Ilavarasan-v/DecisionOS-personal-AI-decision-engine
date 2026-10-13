"""
Pydantic schemas for preference create/read/update payloads.
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class PreferenceBase(BaseModel):
    criterion: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Preference criterion, e.g. price, performance, location",
    )

    weight: float = Field(
        1.0,
        ge=0.0,
        le=1.0,
        description="Relative importance, 0.0 - 1.0",
    )

    direction: Literal["maximize", "minimize"] = Field(
        "maximize",
        description="Whether higher or lower values are preferred",
    )

    source: str = Field(
        "user",
        max_length=50,
        description="Where the preference came from",
    )

    confidence: float = Field(
        0.5,
        ge=0.0,
        le=1.0,
        description="Confidence in the preference",
    )


class PreferenceCreate(PreferenceBase):
    user_id: str


class PreferenceUpdate(BaseModel):
    criterion: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
    )

    weight: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
    )

    direction: Optional[Literal["maximize", "minimize"]] = None

    source: Optional[str] = Field(
        None,
        max_length=50,
    )

    confidence: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
    )


class PreferenceRead(PreferenceBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime