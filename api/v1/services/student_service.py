import os.path
from typing import Optional

from fastapi import BackgroundTasks
from sqlalchemy import delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from starlette import status
from starlette.concurrency import run_in_threadpool
from starlette.responses import FileResponse

from api.v1.exceptions import (
    StudentImageDeleteError,
    NotFoundException,
    QRCodeDeletionError,
    AlreadyExists,
)
from api.v1.models.enrollment import Enrollment
from api.v1.models.formation import Formation
from api.v1.models.image import Image
from api.v1.models.qrcode import QRCode
from api.v1.models.student import Student, StudentCreate
from api.v1.services.qrcode_service import (
    generate_qrcode,
)
from api.v1.utils import clean_spaces


async def add_student(
    new_student: StudentCreate, session: AsyncSession, bgt: BackgroundTasks
):
    """
    Creates a Student and his QR code, then insert both into the database.
    """

    db_student = Student.model_validate(new_student)
    db_student.name = clean_spaces(db_student.name).title()

    if db_student.email:
        db_student.email = db_student.email.lower()

    session.add(db_student)
    await session.commit()

    qr_code = QRCode()

    qr_img_path = await run_in_threadpool(
        generate_qrcode, str(db_student.id), db_student.id
    )

    qr_code.url = qr_img_path

    session.add(qr_code)

    await session.flush()

    db_student.qrcode = qr_code.id

    session.add(db_student)

    await session.commit()

    return {"Success": "Student created", "id": db_student.id}


async def get_all_students(
    session: AsyncSession,
    order_by: Optional[str] = "-id",
    name_search: Optional[str] = None,
):
    order_columns = {
        "id": Student.id,
        "name": Student.name,
        "birth_date": Student.birth_date,
    }

    if order_by:
        direction = "asc"
        col_key = order_by
        if order_by.startswith("-"):
            direction = "desc"
            col_key = order_by[1:]
    else:
        direction = "desc"
        col_key = "id"

    order_column = order_columns.get(col_key, Student.id)

    stmt = select(Student)

    if name_search:
        stmt = stmt.where(
            func.lower(Student.name).like(f"%{clean_spaces(name_search).lower()}%")
        )

    if direction == "desc":
        stmt = stmt.order_by(order_column.desc())
    else:
        stmt = stmt.order_by(order_column.asc())

    query = await session.execute(stmt)
    results = query.scalars().all()
    return results


async def get_student_by_id(student_id: int, session: AsyncSession):
    """
    Retrieves a Student by ID and returns his data.
    """
    student = await session.get(Student, student_id)
    if not student:
        raise NotFoundException("This student was not found.")

    return student


async def delete_student(student_id: int, session: AsyncSession):
    """
    Deletes a student and his QRCode by his ID.
    """
    student = await session.get(Student, student_id)
    if not student:
        raise NotFoundException("This student was not found.")

    img_id = student.image
    qr_id = student.qrcode

    await session.delete(student)

    if not qr_id:
        raise NotFoundException("QR Code was not found in DB.")

    qr = await session.get(QRCode, qr_id)
    try:
        if os.path.exists(qr.url):
            os.remove(qr.url)
        else:
            raise QRCodeDeletionError()
    except:
        raise QRCodeDeletionError()

    stmt_del_qr = delete(QRCode).where(QRCode.id == qr_id)
    await session.execute(stmt_del_qr)

    if img_id:
        img = await session.get(Image, img_id)
        try:
            if os.path.exists(img.url):
                os.remove(img.url)
            else:
                raise StudentImageDeleteError()
        except:
            raise StudentImageDeleteError()

        stmt_del_img = delete(Image).where(Image.id == img_id)
        await session.execute(stmt_del_img)

    await session.commit()
    return {"Success": "Student deleted"}


async def update_student(student_id: int, data: StudentCreate, session: AsyncSession):
    student = await session.get(Student, student_id)
    if not student:
        raise NotFoundException("This student was not found.")

    data.name = clean_spaces(data.name).title()

    if data.email:
        data.email = data.email.lower()
    else:
        data.email = None

    student_data = data.model_dump(exclude_unset=True)

    for key, value in student_data.items():
        setattr(student, key, value)

    session.add(student)
    await session.commit()

    return {"Success": "Student updated."}


async def get_qr_code(student_id: int, session: AsyncSession):
    """
    Retrieves the QR Code of a student and returns it.
    """
    student = await session.get(Student, student_id)
    if not student:
        raise NotFoundException("This student was not found.")

    qrcode = await session.get(QRCode, student.qrcode)
    if not qrcode:
        raise NotFoundException("This student was not found.")

    if not os.path.exists(qrcode.url):
        raise NotFoundException("QR Code image was not found.")

    return FileResponse(
        status_code=status.HTTP_200_OK,
        media_type="image/webp",
        path=qrcode.url,
    )


async def enroll(student_id, formation_id, session: AsyncSession):
    st = await session.get(Student, student_id)
    if not st:
        raise NotFoundException("This student was not found.")

    f = await session.get(Formation, formation_id)
    if not f:
        raise NotFoundException("This formation was not found.")

    enr = await session.get(Enrollment, (student_id, formation_id))
    if enr:
        raise AlreadyExists("This enrollment was already created.")

    enrollment: Enrollment = Enrollment()
    enrollment.student_id = student_id
    enrollment.formation_id = formation_id
    session.add(enrollment)
    await session.commit()
    return {"Success": "Enrollment created"}


async def remove_enrollment_from_student(
    student_id, formation_id, session: AsyncSession
):
    st = await session.get(Student, student_id)
    if not st:
        raise NotFoundException("This student was not found.")

    f = await session.get(Formation, formation_id)
    if not f:
        raise NotFoundException("This formation was not found.")

    enr = await session.get(Enrollment, (student_id, formation_id))
    if not enr:
        raise AlreadyExists("This enrollment was not found.")

    await session.delete(enr)
    await session.commit()
    return {"Success": "Enrollment deleted"}
