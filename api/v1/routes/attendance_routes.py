"""
Attendance route definition module.

All routes that are associated with student's attendance records are here.
"""

from datetime import date
from sys import prefix

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from watchfiles import awatch

from api.v1.models.attendance import Attendance, AttendanceCreate
from api.v1.services.attendance_service import add_attendance
from db.session import get_session

router = APIRouter(prefix="/attendances", tags=["Attendance"])


@router.post("/add", status_code=status.HTTP_201_CREATED)
async def add(
    attendance: AttendanceCreate, session: AsyncSession = Depends(get_session)
):
    return await add_attendance(attendance, session)
