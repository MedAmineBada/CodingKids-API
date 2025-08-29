from typing import List, Optional

from fastapi import APIRouter, Depends
from fastapi.params import Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_201_CREATED, HTTP_200_OK

from api.v1.models.teacher import TeacherModel, Teacher
from api.v1.services.teacher_service import (
    add_teacher,
    get_teachers,
    delete_teacher,
    update_teacher,
    get_teacher_by_id,
)
from db.session import get_session

router = APIRouter(prefix="/teachers", tags=["Teacher"])


@router.post("/add", status_code=HTTP_201_CREATED)
async def add(teacher: TeacherModel, session: AsyncSession = Depends(get_session)):
    return await add_teacher(teacher, session)


@router.get("/", status_code=HTTP_200_OK, response_model=List[Teacher])
async def get(
    search: Optional[str] = Query(None),
    order_by: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session),
):
    return await get_teachers(session, search, order_by)


@router.delete("/delete/{teacher_id}", status_code=HTTP_200_OK)
async def delete(teacher_id: int, session: AsyncSession = Depends(get_session)):
    return await delete_teacher(teacher_id, session)


@router.patch("/update/{teacher_id}", status_code=HTTP_200_OK)
async def update(
    teacher_id: int, data: TeacherModel, session: AsyncSession = Depends(get_session)
):
    return await update_teacher(teacher_id, data, session)


@router.get("/{teacher_id}", status_code=HTTP_200_OK, response_model=Teacher)
async def get_by_id(teacher_id: int, session: AsyncSession = Depends(get_session)):
    return await get_teacher_by_id(teacher_id, session)
