"""
Formation Table Model

Defines the `Formation` table with core fields and validation logic.
"""

from typing import Optional

import unicodedata
from pydantic import BaseModel, field_validator
from sqlmodel import SQLModel, Field

from api.v1.utils import remove_spaces

MAX_LABEL_LENGTH = 100


def is_valid_label(label: str) -> bool:
    """Return True if label is acceptable (not empty after trim and no control chars)."""
    if not label or not remove_spaces(label):
        return False

    for ch in label:
        if unicodedata.category(ch).startswith("C"):  # Control chars (Cc, Cf, etc.)
            return False

    return True


class FormationModel(BaseModel):
    label: str

    class Config:
        orm_mode = True

    @field_validator("label")
    @classmethod
    def validate_label(cls, v: str) -> str:
        # Normalize to NFC
        v = unicodedata.normalize("NFC", v)

        if len(v) > MAX_LABEL_LENGTH:
            raise ValueError(f"Label too long (>{MAX_LABEL_LENGTH} chars)")

        if not is_valid_label(v):
            raise ValueError(
                "Label is not valid (empty or contains control characters)"
            )

        return v.strip()


class Formation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    label: str = Field(nullable=False, max_length=MAX_LABEL_LENGTH)
