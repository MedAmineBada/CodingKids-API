from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.exceptions import AlreadyExists
from api.v1.models.teacher import TeacherModel, Teacher
from api.v1.utils import clean_spaces


async def add_teacher(teacher_model: TeacherModel, session: AsyncSession):
    """
    Creates a Teacher, then inserts him into the database.
    """
    db_teacher = await session.get(Teacher, teacher_model.cin)

    if db_teacher:
        raise AlreadyExists("Teacher already exists in database.")

    teacher = Teacher.model_validate(teacher_model)
    teacher.name = clean_spaces(teacher.name).title()

    if teacher.email:
        teacher.email = teacher.email.lower()

    session.add(teacher)
    await session.commit()

    return "Successfully added teacher"
