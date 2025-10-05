from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from api.v1.exceptions import AlreadyExists, NotFoundException
from api.v1.models.teacher import TeacherModel, Teacher
from api.v1.utils import clean_spaces, remove_spaces


async def add_teacher(teacher_model: TeacherModel, session: AsyncSession):
    """
    Creates a Teacher, then inserts him into the database.
    """
    search_stmt = select(Teacher).where(Teacher.cin == teacher_model.cin)
    search_query = await session.execute(search_stmt)
    search_result = search_query.scalars().all()
    if search_result:
        raise AlreadyExists("Teacher already exists in database.")

    teacher = Teacher.model_validate(teacher_model)
    teacher.name = clean_spaces(teacher.name).title()

    if teacher.email:
        teacher.email = teacher.email.lower()

    session.add(teacher)
    await session.commit()
    return {"id": teacher.id}


from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession


async def get_teachers(
    session: AsyncSession, search: Optional[str] = None, order_by: Optional[str] = "-id"
):
    order_columns = {
        "id": Teacher.id,
        "name": Teacher.name,
        "cin": Teacher.cin,
    }

    stmt = select(Teacher)

    if search:
        cleaned_search = remove_spaces(search)
        if cleaned_search.isdigit():
            stmt = stmt.where(func.lower(Teacher.cin).like(f"%{cleaned_search}%"))
        elif cleaned_search.isalpha():
            stmt = stmt.where(
                func.lower(Teacher.name).like(f"%{clean_spaces(search).lower()}%")
            )

    if order_by:
        direction = "asc"
        col_key = order_by
        if order_by.startswith("-"):
            direction = "desc"
            col_key = order_by[1:]
    else:
        direction = "desc"
        col_key = "id"

    order_column = order_columns.get(col_key, Teacher.id)

    if direction == "desc":
        stmt = stmt.order_by(order_column.desc())
    else:
        stmt = stmt.order_by(order_column.asc())

    query = await session.execute(stmt)
    results = query.scalars().all()
    return results


async def delete_teacher(teacher_id: int, session: AsyncSession):
    teacher = await session.get(Teacher, teacher_id)
    if not teacher:
        raise NotFoundException("Teacher not found.")
    else:
        await session.delete(teacher)
        await session.commit()
        return {"Teacher deleted."}


async def update_teacher(teacher_id: int, data: TeacherModel, session: AsyncSession):
    teacher = await session.get(Teacher, teacher_id)
    if not teacher:
        raise NotFoundException("Teacher not found.")

    data.name = clean_spaces(data.name).title()

    if data.email:
        data.email = data.email.lower()
    else:
        data.email = None

    teacher_data = data.model_dump(exclude_unset=True)

    for key, value in teacher_data.items():
        setattr(teacher, key, value)

    session.add(teacher)
    await session.commit()

    return {"Success": "Teacher updated."}


async def get_teacher_by_id(teacher_id: int, session: AsyncSession):
    teacher = await session.get(Teacher, teacher_id)
    if not teacher:
        raise NotFoundException("Teacher not found.")
    else:
        return teacher
