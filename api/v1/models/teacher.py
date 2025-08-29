"""
Teacher Table Model

Defines the `Teacher` table with core fields and validation logic.
"""

from typing import Optional

from fastapi.openapi.models import Contact
from pydantic import model_validator, BaseModel, EmailStr
from sqlalchemy import Column, Integer, ForeignKey
from sqlmodel import Field, SQLModel

from api.v1.utils import verif_str, verif_tel_number, verif_cin


class TeacherModel(BaseModel):
    cin: str
    name: str
    tel: str
    email: Optional[EmailStr] = None
    cv: Optional[int] = None

    class Config:
        orm_mode = True

    @model_validator(mode="after")
    @classmethod
    def validate(self, m: "Contact") -> "Contact":
        """
        Validates that:
        - All required fields (`name`, `tel1`, `tel2`, `birth_date`) are present
        - `name`, `tel1`,`tel2`, `birth_date` each meet their format requirements
        - `tel1` and `tel2` are not identical
        """

        missing = [f for f in ("cin", "name", "tel") if getattr(m, f) is None]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
        if not verif_cin(getattr(m, "cin")):
            raise ValueError(f"Invalid cin value.")
        if not verif_str(getattr(m, "name")):
            raise ValueError("Name does not meet requirements")
        if not verif_tel_number(getattr(m, "tel")):
            raise ValueError("Telephone number 1 does not meet requirements")
        return m


class Teacher(SQLModel, table=True):
    id: int = Field(
        default=None, primary_key=True, index=True, max_length=8, nullable=False
    )
    cin: str = Field(max_length=8, nullable=False)
    name: str = Field(..., nullable=False)
    tel: str = Field(..., max_length=8, nullable=False)
    email: Optional[EmailStr] = Field(default=None)
    cv: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("cvfile.id"),
            nullable=True,
        ),
    )
