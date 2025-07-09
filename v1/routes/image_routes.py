"""
Image route definition module.

All routes that are associated with student's images are here.
"""

from fastapi import APIRouter, UploadFile, File
from fastapi import BackgroundTasks
from fastapi.params import Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status
from watchfiles import awatch

from db.session import get_session
from v1.services.image_service import (
    upload_image,
    get_image,
    replace_image,
    delete_image,
)

router = APIRouter(tags=["images"])


@router.get("/{student_id}/image")
async def get(student_id: int, session: AsyncSession = Depends(get_session)):
    """
    Fetches a student's image by his id
    """
    return await get_image(student_id, session)


@router.post("/{student_id}/image/upload", status_code=status.HTTP_201_CREATED)
async def upload(
    student_id: int,
    bg_task: BackgroundTasks,
    image: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
):
    """
    Handles the upload of and image and its association with a student
    """
    return await upload_image(student_id, image, session, bg_task)


@router.patch("/{student_id}/image/replace", status_code=status.HTTP_200_OK)
async def replace(
    student_id: int,
    bg_task: BackgroundTasks,
    image: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
):
    return await replace_image(student_id, bg_task, image, session)


@router.delete("/{student_id}/image/delete", status_code=status.HTTP_200_OK)
async def delete(
    student_id: int,
    session: AsyncSession = Depends(get_session),
):
    return await delete_image(student_id, session)
