"""
CV File's Table Model

Defines the `CV` File's table using SQLModel.
"""

from typing import Optional

from sqlmodel import Field, SQLModel


class CVFile(SQLModel, table=True):
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        index=True,
    )
    url: str = Field(default=None, nullable=False)
