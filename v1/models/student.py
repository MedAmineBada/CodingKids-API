from typing import Optional
from sqlmodel import Field, SQLModel


class Student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: str = Field(default=None, nullable=False)
    tel1: str = Field(default=None, nullable=False)
    tel2: str = Field(default=None, nullable=False)

    qrcode: int = Field(default=None, nullable=False, foreign_key="qrcode.id")
