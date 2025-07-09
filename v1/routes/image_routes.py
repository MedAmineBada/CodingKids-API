from http.client import HTTPException

from fastapi.params import Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status
from fastapi import BackgroundTasks

from db.session import get_session
from v1.models.image import Image
from v1.services.image_service import upload_image, get_image
from fastapi import APIRouter, UploadFile, File

router = APIRouter(tags=["images"])


@router.get("/{student_id}/image")
async def get(student_id: int, session: AsyncSession = Depends(get_session)):
    return await get_image(student_id, session)


@router.post("/{student_id}/image/upload", status_code=status.HTTP_201_CREATED)
async def upload(
    student_id: int,
    bg_task: BackgroundTasks,
    image: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
):
    return await upload_image(student_id, image, session, bg_task)
