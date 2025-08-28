from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_201_CREATED

from api.v1.models.teacher import TeacherModel
from api.v1.services.teacher_service import add_teacher
from db.session import get_session

router = APIRouter(prefix="/teachers", tags=["Teacher"])


@router.post("/add", status_code=HTTP_201_CREATED)
async def add(teacher: TeacherModel, session: AsyncSession = Depends(get_session)):
    return await add_teacher(teacher, session)
