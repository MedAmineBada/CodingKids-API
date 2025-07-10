import os.path

from fastapi import HTTPException, BackgroundTasks
from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from starlette import status
from starlette.concurrency import run_in_threadpool

from v1.exceptions import StudentNotFoundError, StudentImageDeleteError
from v1.models.image import Image
from v1.models.qrcode import QRCode
from v1.models.student import Student, StudentCreate
from v1.services.qrcode_service import (
    generate_qrcode,
    QRCodeGenerationError,
    QRCodeNotFoundInDBError,
    QRCodeDeletionError,
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
    try:
        db_student = Student.model_validate(new_student)
        db_student.name = db_student.name.title()
        bgt.add_task(background_add_user, db_student, session)
        return {"Success": "Student created"}

    except QRCodeGenerationError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="QR code generation failed.",
        )
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error: could not add user.",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        )


async def get_all_students(session: AsyncSession):
    try:
        stmt = select(Student)
        query = await session.execute(stmt)
        results = query.scalars().all()
        return results

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error: Couldn't fetch students.",
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        )


async def get_student(student_id: int, session: AsyncSession):
    """
    Retrieves a Student by ID and returns his data.
    """
    try:
        student = await session.get(Student, student_id)
        if not student:
            raise StudentNotFoundError()

        return student
    except StudentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student was not found"
        )
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error: could not fetch user.",
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


async def delete_student(student_id: int, session: AsyncSession):
    """
    Deletes a student and his QRCode by his ID.
    """
    try:
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

    except StudentImageDeleteError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Local image was not deleted",
        )
    except StudentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student was not found"
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Local QR Code image was not found",
        )
    except QRCodeNotFoundInDBError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QR Code was not found in database",
        )
    except QRCodeDeletionError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="QR Code Image could not be deleted",
        )
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error: could not delete user.",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        )


async def update_student(student_id: int, data: StudentCreate, session: AsyncSession):
    try:
        student = await session.get(Student, student_id)
        if not student:
            raise StudentNotFoundError()

        student_data = data.model_dump(exclude_unset=True)

        for key, value in student_data.items():
            setattr(student, key, value)

        session.add(student)
        await session.commit()

        return {"Success": "Student updated."}

    except StudentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student was not found"
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        )
