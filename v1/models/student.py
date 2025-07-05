from typing import Optional

from fastapi.openapi.models import Contact
from pydantic import model_validator
from sqlalchemy import ForeignKey, Column, Integer
from sqlmodel import Field, SQLModel

from v1.common_functions import verif_str, verif_tel_number


class Student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: str = Field(..., nullable=False)
    tel1: str = Field(..., max_length=8, nullable=False)
    tel2: str = Field(..., max_length=8, nullable=False)

    qrcode: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("qrcode.id", ondelete="CASCADE", onupdate="CASCADE"),
            nullable=True,
        ),
    )

    @model_validator(mode="after")
    @classmethod
    def not_empty(self, m: "Contact") -> "Contact":
        missing = [f for f in ("name", "tel1", "tel2") if getattr(m, f) is None]
        if getattr(m, "id") or getattr(m, "qrcode"):
            raise ValueError(f"id and qrcode fields are forbidden.")
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
        if not verif_str(getattr(m, "name")):
            raise ValueError("Name does not meet requirements")
        if not verif_tel_number(getattr(m, "tel1")):
            raise ValueError("Telephone number 1 does not meet requirements")
        if not verif_tel_number(getattr(m, "tel2")):
            raise ValueError("Telephone number 2 does not meet requirements")
        if getattr(m, "tel1") == getattr(m, "tel2"):
            raise ValueError("Telephone numbers should not match")
        return m
