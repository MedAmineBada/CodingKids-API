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


class EnrollmentModel(BaseModel):
    student_id: int
    formation_id: int

    class Config:
        orm_mode = True

    @model_validator(mode="after")
    @classmethod
    def validate(self, m: "Contact") -> "Contact":
        """
        Validates that:
        - All fields are present
        - `attendance_date` meets the format requirements
        """

        missing = [f for f in ("student_id", "formation_id") if getattr(m, f) is None]

        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        return m


class Enrollment(SQLModel, table=True):
    student_id: int = Field(
        sa_column=Column(
            ForeignKey("student.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )
    formation_id: int = Field(
        sa_column=Column(
            ForeignKey("formation.id", ondelete="CASCADE", onupdate="CASCADE"),
            primary_key=True,
        ),
    )
