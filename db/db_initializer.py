"""
Database initialization module.

This module is responsible for importing all the SQLModel models so that their
tables are created in the database if they do not exist. .
"""

from sqlmodel import SQLModel

from api.v1.models.attendance import Attendance
from api.v1.models.cvfile import CVFile
from api.v1.models.enrollment import Enrollment
from api.v1.models.formation import Formation
from api.v1.models.formation_type import FormationType
from api.v1.models.image import Image
from api.v1.models.payment import Payment

# Import models to ensure they are registered with SQLModel.metadata
from api.v1.models.qrcode import QRCode
from api.v1.models.sessions import Session
from api.v1.models.student import Student
from api.v1.models.teacher import Teacher
from .engine import creator_engine

# To keep formatters from removing their imports
_models = (
    QRCode,
    Student,
    Image,
    Attendance,
    Payment,
    Teacher,
    CVFile,
    Formation,
    FormationType,
    Enrollment,
    Session,
)


async def init_db():
    """
    Initialize the database using the dedicated engine for table definition.
    After creation, the engine is disposed of to clean up resources.
    """
    async with creator_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    await creator_engine.dispose()
