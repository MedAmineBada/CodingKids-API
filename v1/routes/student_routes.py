"""
Module for defining the `/users/` endpoints: Creation, Fetching, Deletion and Modification.
"""

import json
from io import BytesIO

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status
from starlette.concurrency import run_in_threadpool
from starlette.responses import FileResponse, Response
from aiohttp import MultipartWriter

from db.session import get_session
from v1.models.qrcode import QRCode
from v1.models.student import Student, StudentCreate, StudentRead
from v1.services.qrcode_service import generate_qrcode, QRCodeGenerationError

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("/add", tags=["Students"])
async def add_user(
    student: StudentCreate, session: AsyncSession = Depends(get_session)
):
    """
    Creates a Student and his QR code, then insert both into the database.
    """
    try:
        db_student = Student.model_validate(student)
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


@router.get("/{id}", response_model=StudentRead, tags=["Students"])
async def get_user(id: int, session: AsyncSession = Depends(get_session)):
    """
    Retrieves a Student by ID and returns a multipart response:
    - JSON student data
    - WEBP QR Code image
    """
    try:
        student = await session.get(Student, id)
        if not student:
            raise StudentNotFound()

        return student
    except StudentNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student was not found"
        )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
