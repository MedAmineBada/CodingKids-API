"""
Module for defining the `/users/` endpoints: Creation, Fetching, Deletion and Modification.
"""

import threading

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status
from starlette.concurrency import run_in_threadpool

from db.session import get_session
from v1.models.qrcode import QRCode
from v1.models.student import Student
from v1.services.qrcode_service import generate_qrcode, QRCodeGenerationError

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("/add", tags=["Students"], status_code=status.HTTP_201_CREATED)
async def add_user(student: Student, session: AsyncSession = Depends(get_session)):
    """
    Creates a Student and his QR code, then insert both into the database.
    """
    try:
        session.add(student)
        await session.flush()

        qr_img = await run_in_threadpool(generate_qrcode, student.name, student.id)
        qr_code = QRCode()
        qr_code.url = qr_img
        qr_code.student = student.id
        session.add(qr_code)
        await session.flush()

        student.qrcode = qr_code.id
        await session.commit()
        await session.refresh(student)

        return {"Message": "User added and Qr code generated successfully."}

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
