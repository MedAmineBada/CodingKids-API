from sqlmodel import select, and_
from sqlmodel.ext.asyncio.session import AsyncSession

from api.v1.exceptions import AlreadyExists, NotFoundException
from api.v1.models.attendance import Attendance, AttendanceModel
from api.v1.models.student import Student


async def add_attendance(attendance_model: AttendanceModel, session: AsyncSession):
    attendance = await session.get(
        Attendance, [attendance_model.student_id, attendance_model.attend_date]
    )
    if attendance:
        raise AlreadyExists("Student already attended on this date.")

    student = await session.get(Student, attendance_model.student_id)
    if not student:
        raise NotFoundException()

    att = Attendance.model_validate(attendance_model)

    session.add(att)
    await session.commit()
    return {"success": "Attendance added successfully."}


async def get_attendances(student_id: int, session: AsyncSession):
    stmt = (
        select(Attendance)
        .where(Attendance.student_id == student_id)
        .order_by(Attendance.attend_date.desc())
    )
    res = await session.execute(stmt)
    attendances = res.scalars().all()

    if not attendances:
        raise NotFoundException("No attendances found for this student.")

    # Convert dates to string
    return [att.attend_date.isoformat() for att in attendances]


async def delete_attendance(attendance_model: AttendanceModel, session: AsyncSession):
    stmt = select(Attendance).where(
        and_(
            Attendance.student_id == attendance_model.student_id,
            Attendance.attend_date == attendance_model.attend_date,
        )
    )
    res = await session.execute(stmt)
    result = res.scalars().first()
    if not result:
        raise NotFoundException("No attendances found for this student on this date.")
    await session.delete(result)
    await session.commit()
    return {"success": "Attendance deleted successfully."}
