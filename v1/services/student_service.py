import os.path
from typing import Optional

from fastapi import BackgroundTasks
from sqlalchemy import delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from starlette import status
from starlette.concurrency import run_in_threadpool
from starlette.responses import FileResponse

from v1.exceptions import (
    StudentNotFoundError,
    StudentImageDeleteError,
    QRCodeNotFoundError,
    QRCodeDeletionError,
)
from v1.models.image import Image
from v1.models.qrcode import QRCode
from v1.models.student import Student, StudentCreate
from v1.services.qrcode_service import (
    generate_qrcode,
    QRCodeNotFoundInDBError,
)


async def background_add_user(student: Student, session: AsyncSession):
    """
    This function handles the background tasks for adding students to the database.
    Helps with response times.
    """
    session.add(student)
    await session.flush()

    qr_img_path = await run_in_threadpool(generate_qrcode, student.name, student.id)

    qr_code = QRCode()
    qr_code.url = qr_img_path

    session.add(qr_code)
    await session.flush()

    student.qrcode = qr_code.id
    await session.commit()


async def add_student(
    new_student: StudentCreate, session: AsyncSession, bgt: BackgroundTasks
):
    """
    Creates a Student and his QR code, then insert both into the database.
    """
    db_student = Student.model_validate(new_student)
    db_student.name = db_student.name.title()
    bgt.add_task(background_add_user, db_student, session)
    return {"Success": "Student created"}


async def get_all_students(
    session: AsyncSession,
    order_by: Optional[str] = "name",
    name_search: Optional[str] = None,
):
    order_columns = {
        "name": Student.name,
        "birth_date": Student.birth_date,
    }
    order_column = order_columns.get(order_by, Student.name)

    stmt = select(Student)

    if name_search:
        stmt = stmt.where(func.lower(Student.name).like(f"%{name_search.lower()}%"))

    stmt = stmt.order_by(order_column)

    query = await session.execute(stmt)
    results = query.scalars().all()
    return results


async def get_student(student_id: int, session: AsyncSession):
    """
    Retrieves a Student by ID and returns his data.
    """
    student = await session.get(Student, student_id)
    if not student:
        raise StudentNotFoundError()

    return student


async def delete_student(student_id: int, session: AsyncSession):
    """
    Deletes a student and his QRCode by his ID.
    """
    student = await session.get(Student, student_id)
    if not student:
        raise StudentNotFoundError()

    img_id = student.image
    qr_id = student.qrcode

    await session.delete(student)

    if not qr_id:
        raise QRCodeNotFoundInDBError()

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
        raise StudentNotFoundError()

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
        raise StudentNotFoundError()

    qrcode = await session.get(QRCode, student.qrcode)
    if not qrcode:
        raise QRCodeNotFoundInDBError()

    if not os.path.exists(qrcode.url):
        raise QRCodeNotFoundError()

    return FileResponse(
        status_code=status.HTTP_200_OK,
        media_type="image/webp",
        path=qrcode.url,
    )
