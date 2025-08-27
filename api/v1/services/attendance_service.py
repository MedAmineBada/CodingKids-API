from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.v1.exceptions import AlreadyExists, NotFoundException
from api.v1.models.attendance import Attendance, AttendanceModel
from api.v1.models.student import Student


async def add_attendance(attendance: AttendanceModel, session: AsyncSession):
    attendance = await session.get(
        Attendance, [attendance.student_id, attendance.attend_date]
    )
    if attendance:
        raise AlreadyExists("Student already attended on this date.")
    student = await session.get(Student, attendance.student_id)
    if not student:
        raise NotFoundException()

    att = Attendance.model_validate(attendance)

    session.add(att)
    await session.commit()
    return {"success": "Attendance added successfully"}


async def get_attendances(student_id: int, session: AsyncSession):
    stmt = (
        select(Attendance)
        .where(Attendance.student_id == student_id)
        .order_by(Attendance.attend_date.desc())
    )
    res = await session.execute(stmt)
    if not res:
        raise NotFoundException("No attendances found for this student.")
    return res.scalars().all()
