"""
Student Image Table Model

Defines the `Image` table using SQLModel.
"""

from typing import Optional

from sqlmodel import Field, SQLModel


class Image(SQLModel, table=True):
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        index=True,
    )
    url: str = Field(default=None, nullable=False)
