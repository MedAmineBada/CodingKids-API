"""
Database initialization module.

This module is responsible for importing all the SQLModel models so that their
tables are created in the database if they do not exist. .
"""

from sqlmodel import SQLModel
from .engine import creator_engine

# Import models to ensure they are registered with SQLModel.metadata
from v1.models.qrcode import QRCode
from v1.models.student import Student


async def init_db():
    """
    Initialize the database using the dedicated engine for table definition.
    After creation, the engine is disposed of to clean up resources.
    """
    async with creator_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    await creator_engine.dispose()
