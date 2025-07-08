"""
QR Code Table Model

Defines the `QRCode` table using SQLModel.
"""

from typing import Optional

from sqlalchemy import Column, Integer, ForeignKey
from sqlmodel import Field, SQLModel


class QRCode(SQLModel, table=True):
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        index=True,
    )
    url: str = Field(default=None, nullable=False)
