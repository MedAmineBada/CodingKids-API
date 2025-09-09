"""
Payment Table Model

Defines the `Payment` table using SQLModel.
"""

from datetime import date

from fastapi.openapi.models import Contact
from pydantic import BaseModel, field_validator, model_validator
from sqlalchemy import Column
from sqlmodel import SQLModel, Field, ForeignKey

from api.v1.exceptions import DateNotValid
from api.v1.utils import valid_date, valid_month, valid_year


class PaymentModel(BaseModel):
    student_id: int
    month: int
    year: int
    payment_date: date
    amount: float

    class Config:
        orm_mode = True

    @field_validator("payment_date", mode="before")
    @classmethod
    def _parse_payment_date(cls, v):
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
        - `payment_date` meets the format requirements
        """

        missing = [
            f
            for f in ("student_id", "month", "year", "payment_date", "amount")
            if getattr(m, f) is None
        ]

        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
        if not valid_month(getattr(m, "month")):
            raise ValueError(f"Invalid month: {getattr(m, 'month')}")
        if not valid_year(getattr(m, "year")):
            raise ValueError(f"Invalid year: {getattr(m, 'year')}")
        if not valid_date(getattr(m, "payment_date")):
            raise DateNotValid()
        if getattr(m, "amount") < 0:
            raise ValueError(f"Amount must be Positive: {getattr(m, 'amount')}")
        return m


class Payment(SQLModel, table=True):
    student_id: int = Field(
        sa_column=Column(
            ForeignKey("student.id", ondelete="CASCADE"),
            primary_key=True,
            index=True,
        ),
    )
    month: int = Field(primary_key=True, index=True)
    year: int = Field(primary_key=True, index=True)
    payment_date: date = Field(default=None, nullable=False)
    amount: float = Field(default=None, nullable=False)


class PaymentDates(BaseModel):
    payment_date: date

    class Config:
        orm_mode = True
