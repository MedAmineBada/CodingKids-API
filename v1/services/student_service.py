from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.concurrency import run_in_threadpool
from starlette.responses import FileResponse

from v1.models.qrcode import QRCode
from v1.models.student import Student, StudentCreate
from v1.services.qrcode_service import (
    generate_qrcode,
    QRCodeGenerationError,
    QRCodeNotFoundInDB,
    QRCodeDeletionError,
    delete_qr,
)


async def add_student(new_student: StudentCreate, session: AsyncSession):
    """
    Creates a Student and his QR code, then insert both into the database.
    """
    try:
        db_student = Student.model_validate(new_student)
        db_student.name = db_student.name.title()
        session.add(db_student)
        await session.flush()

        qr_img_path = await run_in_threadpool(
            generate_qrcode, db_student.name, db_student.id
        )

        qr_code = QRCode()
        qr_code.url = qr_img_path
        qr_code.student = db_student.id

        session.add(qr_code)
        await session.flush()

        db_student.qrcode = qr_code.id
        await session.commit()

        return FileResponse(
            status_code=status.HTTP_201_CREATED,
            media_type="image/webp",
            path=qr_img_path,
        )

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


class StudentNotFound(Exception):
    pass


async def get_student(student_id: int, session: AsyncSession):
    """
    Retrieves a Student by ID and returns his data.
    """
    try:
        student = await session.get(Student, student_id)
        if not student:
            raise StudentNotFound()

        return student
    except StudentNotFound:
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
            raise StudentNotFound()

        qr_id = student.qrcode

        await session.delete(student)
        await delete_qr(qr_id, session)

        await session.commit()

        return {"Success": "User deleted."}

    except StudentNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student was not found"
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="QR Code image was not found"
        )
    except QRCodeNotFoundInDB:
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
