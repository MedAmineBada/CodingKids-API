"""
Module for defining the `/users/` endpoints: Creation, Fetching, Deletion and Modification.
"""

from typing import List

from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi.params import Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from db.session import get_session
from v1.models.student import StudentCreate, StudentRead
from v1.services.student_service import (
    add_student,
    get_student,
    delete_student,
    update_student,
    get_all_students,
)
from . import image_routes

router = APIRouter(prefix="/students", tags=["Students"])
router.include_router(image_routes.router)


@router.get(
    "/",
    response_model=List[StudentRead],
    status_code=status.HTTP_200_OK,
    tags=["Students"],
)
async def get_all(session: AsyncSession = Depends(get_session)):
    """
    Returns all students in the database.
    """
    return await get_all_students(session)


@router.get("/{id}", response_model=StudentRead, tags=["Students"])
async def get(id: int, session: AsyncSession = Depends(get_session)):
    """
    Handles the retrieval of a student.
    """
    return await get_student(id, session)


@router.post("/add", status_code=status.HTTP_200_OK, tags=["Students"])
async def add(
    student: StudentCreate,
    bgtask: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    """
    Handles the creation of a new student.
    """
    return await add_student(student, session, bgtask)


@router.delete("/{id}/delete", status_code=status.HTTP_200_OK, tags=["Students"])
async def delete(id: int, session: AsyncSession = Depends(get_session)):
    """
    Handles the deletion of a student.
    """
    return await delete_student(id, session)


@router.patch("/{id}/update", status_code=status.HTTP_200_OK, tags=["Students"])
async def update(
    id: int, new_data: StudentCreate, session: AsyncSession = Depends(get_session)
):
    """
    Handles the update of a student's information.
    """
    return await update_student(id, new_data, session)
