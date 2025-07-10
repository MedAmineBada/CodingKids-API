import io
import os
import time

from PIL import Image as PILImage
from fastapi import UploadFile, HTTPException, BackgroundTasks
from sqlalchemy import delete
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status
from starlette.responses import FileResponse

from envconfig import EnvFile
from v1.exceptions import (
    StudentImageReplaceError,
    StudentImageNotFoundError,
)
from v1.models.image import Image
from v1.models.student import Student
from v1.services.student_service import StudentNotFoundError
from v1.utils import StudentImageSaveError, compress_img


def background_img_save(image, output_path):
    """
    A background task that handles image saving and compression.
    Cuts down immensely on response times.
    """
    temp_path = f"{EnvFile.STUDENT_IMAGE_SAVE_DIR}/TEMP-{time.time()}.webp"
    image.save(temp_path, format="WEBP")
    compress_img(temp_path, output_path)
    os.remove(temp_path)


async def get_image(student: int, session: AsyncSession):
    """
    Handles the fetching of a student's image from the database
    """
    student = await session.get(Student, student)
    if not student:
        raise StudentNotFoundError()

    img: Image = await session.get(Image, student.image)

    if not img:
        raise StudentImageNotFoundError()

    return FileResponse(
        status_code=status.HTTP_200_OK,
        media_type="image/webp",
        path=img.url,
    )


async def upload_image(
    student_id: int,
    file: UploadFile,
    session: AsyncSession,
    bg_task: BackgroundTasks,
):
    """
    A function that handles the uploading of a student image and its insertion into the db
    and association to a student.
    """
    path = f"{EnvFile.STUDENT_IMAGE_SAVE_DIR}/AV{student_id}-{time.time()}.webp"
    st = await session.get(Student, student_id)
    if not st:
        raise StudentNotFoundError()

    if st.image:
        old = await session.get(Image, st.image)
        if os.path.isfile(old.url):
            os.remove(old.url)

        stmt = delete(Image).where(Image.id == old.id)
        await session.execute(stmt)

    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type.",
        )
    img = Image(url=path)

    try:
        image_bytes = await file.read()
        image = PILImage.open(io.BytesIO(image_bytes))
    except:
        raise StudentImageSaveError()

    bg_task.add_task(background_img_save, image, path)

    st.image = None
    await session.flush()

    session.add(img)
    await session.flush()
    st.image = img.id
    await session.commit()

    return {"Success": "Image uploaded successfully"}


async def replace_image(
    student_id: int,
    bg_task: BackgroundTasks,
    file: UploadFile,
    session: AsyncSession,
):
    """
    Replaces a student's image.
    If the student doesn't have an image, a new one i added.
    """
    student = await session.get(Student, student_id)

    if not student:
        raise StudentNotFoundError()

    stmt = select(Image).where(Image.id == student.image)
    old_img_query = await session.execute(stmt)
    old_img: Image = old_img_query.scalar()

    new_path = f"{EnvFile.STUDENT_IMAGE_SAVE_DIR}/AV{student_id}-{time.time()}.webp"

    try:
        image_bytes = await file.read()
        image = PILImage.open(io.BytesIO(image_bytes))
    except:
        raise StudentImageReplaceError()

    bg_task.add_task(background_img_save, image, new_path)
    if old_img:
        os.remove(old_img.url)
        old_img.url = new_path
        session.add(old_img)
    else:
        new_img = Image(url=new_path)
        session.add(new_img)
        await session.flush()
        await session.refresh(new_img)

        student.image = new_img.id
        session.add(student)
    await session.commit()
    return {"success": "image replaced"}


async def delete_image(
    student_id: int,
    session: AsyncSession,
):
    student = await session.get(Student, student_id)
    if not student:
        raise StudentNotFoundError()

    if student.image:
        img_id = student.image
        img = await session.get(Image, img_id)

        if img:
            # Remove DB link and image record
            student.image = None
            await session.delete(img)
            session.add(student)

            # Try to delete the image file (if it exists)
            if os.path.exists(img.url):
                os.remove(img.url)

        await session.commit()

    return {"success": "Image deleted"}
