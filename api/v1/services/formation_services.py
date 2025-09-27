from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from api.v1.exceptions import AlreadyExists, NotFoundException
from api.v1.models.formation import FormationModel, Formation
from api.v1.models.formation_record import FormationRecordModel, FormationRecord


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


async def add_formation_record(record: FormationRecordModel, session: AsyncSession):
    formation = await session.get(Formation, record.formation_id)
    if not formation:
        raise NotFoundException("No formation with this id found.")
    db_record = await session.get(FormationRecord, (record.formation_id, record.year))
    if db_record:
        raise AlreadyExists("A record with this formation and year already exists.")
    f_rec = FormationRecord.model_validate(record)
    f_rec.formation_label = formation.label
    session.add(f_rec)
    await session.commit()
    return "Record added."


async def get_formation_records(session: AsyncSession):
    stmt = select(FormationRecord)
    query = await session.execute(stmt)
    result = query.scalars().all()

    return result


async def delete_formation_record(record: FormationRecordModel, session: AsyncSession):
    record = await session.get(FormationRecord, (record.formation_id, record.year))
    if not record:
        raise NotFoundException("No formation record with this id and year found.")
    await session.delete(record)
    await session.commit()
    return "Record deleted."


async def update_formation_record(
    old: FormationRecordModel, new: FormationRecordModel, session: AsyncSession
):
    record = await session.get(FormationRecord, (old.formation_id, old.year))
    if not record:
        raise NotFoundException("No formation record with this id and year found.")

    if old.formation_id != new.formation_id:
        formation = await session.get(Formation, old.formation_id)
        if not formation:
            raise NotFoundException("No formation with this id found (old formation).")

        new_formation = await session.get(Formation, new.formation_id)
        if not new_formation:
            raise NotFoundException("No formation with this id found (new formation).")

        record.formation_id = new.formation_id
        record.formation_label = new_formation.label

    if old.year != new.year:
        record.year = new.year

    session.add(record)
    await session.commit()
    return "Record updated."
