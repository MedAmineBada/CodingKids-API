"""
Attendance Table Model

Defines the `Attendance` table using SQLModel.
"""

from datetime import date

from fastapi.openapi.models import Contact
from pydantic import BaseModel, field_validator, model_validator
from sqlalchemy import Column
from sqlmodel import SQLModel, Field, ForeignKey

from api.v1.exceptions import DateNotValid
from api.v1.utils import valid_date


class SessionModel(BaseModel):
    teacher_id: int
    session_date: date

    class Config:
        orm_mode = True

    @field_validator("session_date", mode="before")
    @classmethod
    def _parse_attend_date(cls, v):
        if isinstance(v, str):
            # throw error if the format is wrong
            return date.fromisoformat(v)
        return v

    @model_validator(mode="after")
    @classmethod
    def validate(self, m: "Contact") -> "Contact":
        """
        Validates that:
        - All fields are present
        - `attendance_date` meets the format requirements
        """

        missing = [f for f in ("teacher_id", "session_date") if getattr(m, f) is None]

        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        if not valid_date(getattr(m, "session_date")):
            raise DateNotValid()

        return m


class Session(SQLModel, table=True):
    teacher_id: int = Field(
        sa_column=Column(
            ForeignKey("teacher.id", ondelete="CASCADE"),
            primary_key=True,
            index=True,
        ),
    )
    session_date: date = Field(primary_key=True, index=True)


class SessionDate(BaseModel):
    session_date: date

    class Config:
        orm_mode = True
