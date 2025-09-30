from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, and_

from api.v1.exceptions import AlreadyExists, NotFoundException
from api.v1.models.formation import FormationModel, Formation
from api.v1.models.formation_type import FormationType, FormationTypeModel


async def get_formations(session: AsyncSession):
    stmt = select(
        Formation.id,
        Formation.start_date,
        Formation.formation_type,
        FormationType.label,
    ).join(FormationType, Formation.formation_type == FormationType.id)

    result = await session.execute(stmt)
    rows = []
    for id, start_date, formation_type, label in result:
        rows.append(
            {
                "id": id,
                "formation_type": formation_type,
                "label": label,
                "start_date": start_date,
            }
        )
    return rows


async def add_formation(formation: FormationModel, session: AsyncSession):
    ft = await session.get(FormationType, formation.formation_type)
    if not ft:
        raise NotFoundException("Formation type not found.")

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
