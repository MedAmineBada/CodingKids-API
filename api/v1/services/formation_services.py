from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, and_

from api.v1.exceptions import AlreadyExists, NotFoundException
from api.v1.models.enrollment import Enrollment
from api.v1.models.formation import FormationModel, Formation
from api.v1.models.formation_type import FormationType, FormationTypeModel
from api.v1.models.teacher import Teacher


async def get_formations(session: AsyncSession):
    stmt = (
        select(
            Formation.id,
            Formation.start_date,
            Formation.formation_type,
            FormationType.label,
            Teacher.name.label("teacher_name"),
        )
        .join(FormationType, Formation.formation_type == FormationType.id)
        .outerjoin(Teacher, Formation.teacher_id == Teacher.id)
    )

    result = await session.execute(stmt)
    rows = []
    # result returns rows that can be unpacked in the same order as the select()
    for id_, start_date, formation_type, label, teacher_name in result:
        rows.append(
            {
                "id": id_,
                "formation_type": formation_type,
                "label": label,
                "start_date": start_date,
                "teacher_name": teacher_name,  # will be None when no teacher is assigned
            }
        )
    return rows


async def add_formation(formation: FormationModel, session: AsyncSession):
    ft = await session.get(FormationType, formation.formation_type)
    if not ft:
        raise NotFoundException("Formation type not found.")

    if formation.teacher_id:
        teacher = await session.get(Teacher, formation.teacher_id)
        if not teacher:
            raise NotFoundException("Teacher not found.")
    print(formation.teacher_id)

    stmt = select(Formation).where(
        and_(
            Formation.formation_type == formation.formation_type,
            Formation.start_date == formation.start_date,
        )
    )
    req = await session.execute(stmt)
    res = req.scalars().first()

    if res:
        raise AlreadyExists("A formation with this label already exists.")

    f: Formation = Formation.model_validate(formation)
    session.add(f)
    await session.commit()
    return {"id": f.id}


async def delete_formation(id: int, session: AsyncSession):
    formation = await session.get(Formation, id)
    if not formation:
        raise NotFoundException("No formation with this id found.")

    await session.delete(formation)
    await session.commit()
    return "Formation deleted."


async def update_formation(id: int, data: FormationModel, session: AsyncSession):
    formation = await session.get(Formation, id)
    if not formation:
        raise NotFoundException("No formation with this id found.")

    if formation.start_date != data.start_date:
        formation.start_date = data.start_date

    if formation.formation_type != data.formation_type:
        formation.formation_type = data.formation_type

    if data.teacher_id:
        teacher = await session.get(Teacher, data.teacher_id)
        if not teacher:
            raise NotFoundException("Teacher not found.")
        formation.teacher_id = teacher.id
    else:
        formation.teacher_id = None

    await session.commit()
    return "Formation updated."


async def get_formation_types(session: AsyncSession):
    stmt = select(FormationType)
    result = await session.execute(stmt)
    return result.scalars().all()


async def add_formation_type(data: FormationTypeModel, session: AsyncSession):
    stmt = select(FormationType).where(FormationType.label == data.label)
    result = await session.execute(stmt)
    if result.scalars().first():
        raise AlreadyExists("A formation type with this label already exists.")
    data.label = data.label.title()
    ftype = FormationType.model_validate(data)
    session.add(ftype)
    await session.commit()
    return {"id": ftype.id}


async def delete_formation_type(id: int, session: AsyncSession):
    ft = await session.get(FormationType, id)
    if not ft:
        raise NotFoundException("No formation type with this id found.")

    await session.delete(ft)
    await session.commit()
    return "Formation type deleted."


async def rename_formation_type(
    id: int, data: FormationTypeModel, session: AsyncSession
):
    ft = await session.get(FormationType, id)
    if not ft:
        raise NotFoundException("No formation type with this id found.")

    if data.label != ft.label:
        stmt = select(FormationType.label).where(FormationType.label == data.label)
        res = await session.execute(stmt)
        if res.scalars().first():
            raise AlreadyExists("A formation type with this label already exists.")
        ft.label = data.label.title()
        await session.commit()

    return "Formation type renamed."


async def get_formations_by_teacher(id: int, session: AsyncSession):
    teacher = await session.get(Teacher, id)
    if not teacher:
        raise NotFoundException("Teacher not found.")

    stmt = select(Formation).where(Formation.teacher_id == id)
    query = await session.execute(stmt)
    return query.scalars().all()


async def unassign_formation(teacher_id: int, formation_id: int, session: AsyncSession):
    t = await session.get(Teacher, teacher_id)
    if not t:
        raise NotFoundException("Teacher not found.")

    f = await session.get(Formation, formation_id)
    if not f:
        raise NotFoundException("Formation not found.")

    f.teacher_id = None
    session.add(f)
    await session.commit()
    return "Formation unassigned."


async def assign_formation(teacher_id: int, formation_id: int, session: AsyncSession):
    t = await session.get(Teacher, teacher_id)
    if not t:
        raise NotFoundException("Teacher not found.")

    f = await session.get(Formation, formation_id)
    if not f:
        raise NotFoundException("Formation not found.")

    f.teacher_id = teacher_id
    session.add(f)
    await session.commit()
    return "Formation assigned."


async def get_student_enrolled_formations(session: AsyncSession, student_id: int):
    stmt = (
        select(
            FormationType.label,
            Formation.start_date,
            Teacher.name.label("teacher_name"),
            Formation.id,
        )
        .select_from(Enrollment)
        .join(Formation, Enrollment.formation_id == Formation.id)
        .join(FormationType, Formation.formation_type == FormationType.id)
        .outerjoin(Teacher, Formation.teacher_id == Teacher.id)
        .where(Enrollment.student_id == student_id)
    )

    result = await session.execute(stmt)

    rows = []
    for label, start_date, teacher_name, formation_id in result:
        rows.append(
            {
                "formation_label": label,
                "start_date": start_date,
                "teacher_name": teacher_name,
                "formation_id": formation_id,
            }
        )

    return rows


async def get_available_formations_for_student(session: AsyncSession, student_id: int):
    # Subquery to get formation IDs the student is enrolled in
    enrolled_formations_subquery = (
        select(Enrollment.formation_id)
        .where(Enrollment.student_id == student_id)
        .scalar_subquery()
    )

    stmt = (
        select(
            FormationType.label,
            Teacher.name.label("teacher_name"),
            Formation.start_date,
            Formation.id,
        )
        .join(FormationType, Formation.formation_type == FormationType.id)
        .outerjoin(Teacher, Formation.teacher_id == Teacher.id)
        .where(Formation.id.not_in(enrolled_formations_subquery))
    )

    result = await session.execute(stmt)

    rows = []
    for label, teacher_name, start_date, formation_id in result:
        rows.append(
            {
                "formation_label": label,
                "teacher_name": teacher_name,
                "start_date": start_date,
                "formation_id": formation_id,
            }
        )

    return rows
