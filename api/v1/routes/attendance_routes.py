"""
Attendance route definition module.

All routes that are associated with student's attendance records are here.
"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.v1.models.attendance import AttendanceModel, AttendanceDates
from api.v1.services.attendance_service import add_attendance, get_attendances
from db.session import get_session

router = APIRouter(prefix="/attendances", tags=["Attendance"])


@router.post("/add", status_code=status.HTTP_201_CREATED)
async def add(
    attendance: AttendanceModel, session: AsyncSession = Depends(get_session)
):
    return await add_attendance(attendance, session)


@router.get(
    "/{student_id}",
    response_model=List[AttendanceDates],
    status_code=status.HTTP_200_OK,
)
async def get(student_id: int, session: AsyncSession = Depends(get_session)):
    return await get_attendances(student_id, session)
