"""
Module for defining the `/users/` endpoints: Creation, Fetching, Deletion and Modification.
"""

from fastapi import APIRouter
from fastapi.params import Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from db.session import get_session
from v1.models.student import StudentCreate, StudentRead
from v1.services.student_service import add_student, get_student, delete_student

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("/add", tags=["Students"])
async def add(student: StudentCreate, session: AsyncSession = Depends(get_session)):
    """
    Handles the creation of a new student.
    """
    return await add_student(student, session)


@router.get("/{id}", response_model=StudentRead, tags=["Students"])
async def get(id: int, session: AsyncSession = Depends(get_session)):
    """
    Handles the retrieval of a student.
    """
    return await get_student(id, session)


@router.delete("/delete/{id}", status_code=status.HTTP_200_OK, tags=["Students"])
async def delete(id: int, session: AsyncSession = Depends(get_session)):
    """
    Handles the deletion of a student.
    """
    return await delete_student(id, session)
