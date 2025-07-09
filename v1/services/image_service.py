import io
import os
import time

from fastapi import UploadFile, HTTPException, BackgroundTasks
from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status
from starlette.responses import FileResponse
from PIL import Image as PILImage
from envconfig import EnvFile
from v1.models.image import Image
from v1.models.student import Student
from v1.services.student_service import StudentNotFound
from v1.utils import ImageSaveError, compress_img


def background_img_save(image, output_path):
    try:
        temp_path = f"{EnvFile.STUDENT_IMAGE_SAVE_DIR}/TEMP-{time.time()}.webp"
        image.save(temp_path, format="WEBP")
        compress_img(temp_path, output_path)
        os.remove(temp_path)
    except:
        raise ImageSaveError()


async def get_image(student: int, session: AsyncSession):
    try:
        stmt = select(Image).where(Image.student == student)
        img_query = await session.execute(stmt)
        img: Image = img_query.scalar()

        return FileResponse(
            status_code=status.HTTP_200_OK,
            media_type="image/webp",
            path=img.url,
        )
    except StudentNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student was not found"
        )
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error: could not fetch user image.",
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )


async def upload_image(
    student_id: int,
    file: UploadFile,
    session: AsyncSession,
    bg_task: BackgroundTasks,
):
    try:
        path = f"{EnvFile.STUDENT_IMAGE_SAVE_DIR}/AV{student_id}-{time.time()}.webp"
        st = await session.get(Student, student_id)
        if not st:
            raise StudentNotFound()
        img = Image(url=path, student=student_id)

        getold = select(Image.url).where(Image.student == student_id)
        oldimgs = await session.execute(getold)
        urls = oldimgs.scalars().all()

        for url in urls:
            if os.path.isfile(url):
                os.remove(url)

        # await save_image(file, path)
        if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Unsupported file type.",
            )
        try:
            image_bytes = await file.read()
            image = PILImage.open(io.BytesIO(image_bytes))
        except:
            raise ImageSaveError()

        bg_task.add_task(background_img_save, image, path)

        st.image = None

        stmt = delete(Image).where(Image.student == student_id)
        await session.execute(stmt)

        session.add(img)
        await session.flush()
        st.image = img.id
        await session.commit()

        return {"Success": "Image uploaded successfully"}

    except ImageSaveError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Image not saved"
        )
    except StudentNotFound:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student was not found"
        )
    except SQLAlchemyError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error: could not save image.",
        )
    except Exception as e:
        print(e)
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )
