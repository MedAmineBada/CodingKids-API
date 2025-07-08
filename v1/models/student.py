"""
Student Table Model

Defines the `Student` table with core fields and validation logic.
"""

from typing import Optional

from fastapi.openapi.models import Contact
from pydantic import model_validator, BaseModel, EmailStr, field_validator
from sqlalchemy import ForeignKey, Column, Integer
from sqlmodel import Field, SQLModel
from datetime import date

from v1.utils import verif_str, verif_tel_number, verif_birth_date


class StudentCreate(BaseModel):
    name: str
    birth_date: date
    tel1: str
    tel2: str
    email: Optional[EmailStr] = None

    class Config:
        orm_mode = True

    @field_validator("birth_date", mode="before")
    @classmethod
    def _parse_birth_date(cls, v):
        if isinstance(v, str):
            # throw error if the format is wrong
            return date.fromisoformat(v)
        return v

    @model_validator(mode="after")
    @classmethod
    def validate(self, m: "Contact") -> "Contact":
        """
        Validates that:
        - All required fields (`name`, `tel1`, `tel2`, `birth_date`) are present
        - `name`, `tel1`,`tel2`, `birth_date each meet their format requirements
        - `tel1` and `tel2` are not identical
        """

        missing = [
            f for f in ("name", "birth_date", "tel1", "tel2") if getattr(m, f) is None
        ]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
        if not verif_str(getattr(m, "name")):
            raise ValueError("Name does not meet requirements")
        if not verif_birth_date(getattr(m, "birth_date")):
            raise ValueError("Date of birth does not meet requirements")
        if not verif_tel_number(getattr(m, "tel1")):
            raise ValueError("Telephone number 1 does not meet requirements")
        if not verif_tel_number(getattr(m, "tel2")):
            raise ValueError("Telephone number 2 does not meet requirements")
        if getattr(m, "tel1") == getattr(m, "tel2"):
            raise ValueError("Telephone numbers should not match")
        return m


class StudentRead(BaseModel):
    name: str
    birth_date: date
    tel1: str
    tel2: str
    email: Optional[EmailStr]

    class Config:
        orm_mode = True


class Student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: str = Field(..., nullable=False)
    birth_date: date = Field(..., nullable=False)
    tel1: str = Field(..., max_length=8, nullable=False)
    tel2: str = Field(..., max_length=8, nullable=False)
    email: Optional[EmailStr] = Field(default=None)

    # FK to Image table with cascade on delete/update
    image: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("image.id", ondelete="CASCADE", onupdate="CASCADE"),
            nullable=True,
        ),
    )

    # FK to QRCode table with cascade on delete/update
    qrcode: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("qrcode.id", ondelete="CASCADE", onupdate="CASCADE"),
            nullable=True,
        ),
    )
