"""
Image route definition module.

All routes that are associated with student's images are here.
"""

from fastapi import APIRouter, UploadFile, File
from fastapi import BackgroundTasks
from fastapi.params import Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from db.session import get_session
from v1.services.image_service import upload_image, get_image

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
