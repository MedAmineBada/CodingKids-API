from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from api.v1.exceptions import AlreadyExists, NotFoundException
from api.v1.models.formation import FormationModel, Formation


async def get_formations(session: AsyncSession):
    stmt = select(Formation)
    query = await session.execute(stmt)
    results = query.scalars().all()
    return results


async def add_formation(formation: FormationModel, session: AsyncSession):
    stmt = select(Formation).where(Formation.label == formation.label)
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


async def rename_formation(id: int, data: FormationModel, session: AsyncSession):
    formation = await session.get(Formation, id)
    if not formation:
        raise NotFoundException("No formation with this id found.")

    formation.label = data.label
    await session.commit()
    return "Formation renamed."
