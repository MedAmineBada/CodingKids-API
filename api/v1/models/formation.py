"""
Formation Table Model

Defines the `Formation` table with core fields and validation logic.
"""

from datetime import date, datetime
from typing import Optional

from fastapi.openapi.models import Contact
from pydantic import BaseModel, model_validator
from sqlalchemy import Column, ForeignKey
from sqlmodel import SQLModel, Field

from api.v1.utils import valid_date


class FormationAssignage(BaseModel):
    formation_id: int


class FormationModel(BaseModel):
    formation_type: int
    start_date: date
    teacher_id: Optional[int] = None

    class Config:
        orm_mode = True

    @model_validator(mode="after")
    @classmethod
    def validate(self, m: "Contact") -> "Contact":
        """
        Validates that:
        - All fields are present
        - `start_date` meets the format requirements
        """

        missing = [f for f in ("formation_type", "start_date") if getattr(m, f) is None]

        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
        if not valid_date(getattr(m, "start_date"), year_offset=1):
            raise ValueError(f"Start date is not valid: {getattr(m, 'start_date')}")
        return m


class FormationOut(BaseModel):
    id: int
    title: Optional[str] = None
    description: Optional[str] = None
    # optional fields you might have on Formation
    start_date: Optional[date] = None

    class Config:
        orm_mode = True


class EnrolledFormationOut(BaseModel):
    formation_id: int
    enrolled_at: datetime

    class Config:
        orm_mode = True


class Formation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    formation_type: int = Field(
        sa_column=Column(
            ForeignKey("Formation_Type.id", ondelete="CASCADE", onupdate="CASCADE"),
            default=None,
            nullable=False,
            index=True,
        ),
    )
    start_date: date = Field(default=None, nullable=False)
    teacher_id: Optional[int] = Field(
        sa_column=Column(
            ForeignKey("teacher.id", onupdate="CASCADE"),
            default=None,
            nullable=True,
            index=True,
        ),
    )


class FormationWithTypeOut(BaseModel):
    """Response model combining Formation and FormationType data."""

    # Formation fields
    id: int
    formation_type_id: int
    start_date: date
    teacher_id: Optional[int]
    # FormationType fields
    type_label: str

    class Config:
        orm_mode = True
