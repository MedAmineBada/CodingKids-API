import os
import time
from os.path import exists
from pathlib import Path
from random import randint
from typing import Optional

from fastapi import BackgroundTasks, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from starlette.responses import FileResponse

from api.v1.exceptions import NotFoundException, UnprocessableEntityException
from api.v1.models.cvfile import CVFile
from api.v1.models.teacher import Teacher  # adjust path if needed
from envconfig import EnvFile


def _background_save_pdf(data: bytes, path: str):
    """
    Synchronous background task: write bytes to a temp file then rename.
    """
    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)

    tmp_path = path_obj.with_suffix(path_obj.suffix + ".tmp")
    with tmp_path.open("wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(str(tmp_path), str(path_obj))


async def upload_teacher_cv(
    teacher_id: int,
    bg_task: BackgroundTasks,
    file: UploadFile,
    session: AsyncSession,
):
    """
    Replace or add a teacher's CV and save locally as a PDF.
    """
    if file.content_type != "application/pdf":
        raise UnprocessableEntityException("The file must be pdf file.")
    teacher: Optional[Teacher] = await session.get(Teacher, teacher_id)
    if not teacher:
        raise NotFoundException("This teacher was not found.")

    stmt = select(CVFile).where(CVFile.id == teacher.cv)
    result = await session.execute(stmt)
    old_cv: Optional[CVFile] = result.scalar_one_or_none()

    # read uploaded file bytes
    try:
        pdf_bytes = await file.read()
    except Exception as exc:
        raise ValueError("Failed to read uploaded file.") from exc

    # PDF validation
    if not pdf_bytes or not pdf_bytes.startswith(b"%PDF"):
        raise UnprocessableEntityException("The uploaded file is not a PDF.")

    timestamp = int(time.time())
    filename = f"T{teacher_id}-{timestamp}.pdf"
    new_path = str(Path(EnvFile.CV_SAVE_DIR) / filename)

    # Verify Existance
    while exists(new_path):
        filename = f"T{teacher_id}-{timestamp}-DP-{chr(randint(64, 64 + 26)) + str(randint(0, 999))}.pdf"
        new_path = str(Path(EnvFile.CV_SAVE_DIR) / filename)

    bg_task.add_task(_background_save_pdf, pdf_bytes, new_path)

    if old_cv:
        try:
            if old_cv.url:
                old_path = Path(old_cv.url)
                if old_path.exists():
                    old_path.unlink()
        except Exception:
            pass

        old_cv.url = new_path
        session.add(old_cv)
    else:
        new_cv = CVFile(url=new_path)
        session.add(new_cv)
        await session.flush()
        await session.refresh(new_cv)

        teacher.cv = new_cv.id
        session.add(teacher)

    await session.commit()

    return {"Successfully uploaded CV."}


async def retrieve_cv(teacher_id: int, session: AsyncSession) -> FileResponse | None:
    teacher = await session.get(Teacher, teacher_id)
    if not teacher:
        raise NotFoundException("This teacher was not found.")
    if not teacher.cv:
        return None
    cv = await session.get(CVFile, teacher.cv)
    if not cv:
        return None

    return FileResponse(path=cv.url, media_type="application/pdf")


async def delete_teacher_cv(teacher_id: int, session: AsyncSession):
    teacher = await session.get(Teacher, teacher_id)
    if not teacher:
        raise NotFoundException("This teacher was not found.")
    if not teacher.cv:
        return None

    cv = await session.get(CVFile, teacher.cv)
    if not cv:
        raise NotFoundException("This CV was not found.")

    if not exists(cv.url):
        raise NotFoundException("This CV File was not found.")

    teacher.cv = None
    session.add(teacher)
    await session.commit()

    await session.delete(cv)
    await session.commit()

    os.remove(cv.url)

    return {"Successfully deleted CV."}
