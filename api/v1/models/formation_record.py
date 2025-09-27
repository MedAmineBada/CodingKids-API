"""
Formation_Record Table Model

Defines the `Formation_Record` table with core fields and validation logic.
"""

from typing import Optional

from fastapi.openapi.models import Contact
from pydantic import BaseModel, model_validator
from sqlmodel import SQLModel, Field

from api.v1.utils import valid_year


class FormationRecordModel(BaseModel):
    formation_id: int
    year: int

    class Config:
        orm_mode = True

    @model_validator(mode="after")
    @classmethod
    def validate(self, m: "Contact") -> "Contact":
        missing = [f for f in ("formation_id", "year") if getattr(m, f) is None]

        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
        if not valid_year(getattr(m, "year")):
            raise ValueError(f"Invalid year: {getattr(m, 'year')}")
        return m


class FormationRecord(SQLModel, table=True):
    __tablename__ = "formation_record"
    formation_id: int = Field(primary_key=True)
    year: int = Field(primary_key=True)
    formation_label: Optional[str] = Field(default=None, nullable=True)
