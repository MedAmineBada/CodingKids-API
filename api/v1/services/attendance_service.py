from sqlmodel.ext.asyncio.session import AsyncSession

from api.v1.exceptions import StudentNotFoundError, AlreadyExists
from api.v1.models.attendance import Attendance, AttendanceCreate
from api.v1.models.student import Student


async def add_attendance(attendance: AttendanceCreate, session: AsyncSession):
    attendance = await session.get(
        Attendance, [attendance.student_id, attendance.attend_date]
    )
    if attendance:
        raise AlreadyExists("Student already attended on this date.")
    student = await session.get(Student, attendance.student_id)
    if not student:
        raise StudentNotFoundError()

    att = Attendance.model_validate(attendance)

    session.add(att)
    await session.commit()
    return {"success": "Attendance added successfully"}
