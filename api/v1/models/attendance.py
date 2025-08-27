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


class AttendanceModel(BaseModel):
    student_id: int
    attend_date: date

    class Config:
        orm_mode = True

    @field_validator("attend_date", mode="before")
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
        - All fieldsare present
        - `attendance_date` meets the format requirements
        """

        missing = [f for f in ("student_id", "attend_date") if getattr(m, f) is None]

        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        if not valid_date(getattr(m, "attend_date")):
            raise DateNotValid()

        return m


class Attendance(SQLModel, table=True):
    student_id: int = Field(
        sa_column=Column(
            ForeignKey("student.id", ondelete="CASCADE"),
            primary_key=True,
            index=True,
        ),
    )
    attend_date: date = Field(primary_key=True, index=True)


class AttendanceDates(BaseModel):
    attend_date: date

    class Config:
        orm_mode = True
