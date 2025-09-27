"""
Formation route definition module.

All routes that are associated with formations are here.
"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.v1.models.formation import FormationModel, Formation
from api.v1.models.formation_record import FormationRecordModel, FormationRecord
from api.v1.services.formation_services import (
    add_formation,
    get_formations,
    delete_formation,
    rename_formation,
    add_formation_record,
    delete_formation_record,
    get_formation_records,
    update_formation_record,
)
from db.session import get_session

router = APIRouter(prefix="/formations")


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[Formation])
async def get(session: AsyncSession = Depends(get_session)):
    return await get_formations(session)


@router.post("/add", status_code=status.HTTP_201_CREATED)
async def add(formation: FormationModel, session: AsyncSession = Depends(get_session)):
    return await add_formation(formation, session)


@router.delete("/delete/{id}", status_code=status.HTTP_200_OK)
async def delete(id: int, session: AsyncSession = Depends(get_session)):
    return await delete_formation(id, session)


@router.patch("/rename/{id}", status_code=status.HTTP_200_OK)
async def rename(
    id: int, data: FormationModel, session: AsyncSession = Depends(get_session)
):
    return await rename_formation(id, data, session)


@router.get(
    "/records", status_code=status.HTTP_200_OK, response_model=List[FormationRecord]
)
async def get_records(session: AsyncSession = Depends(get_session)):
    return await get_formation_records(session)


@router.post("/records/add", status_code=status.HTTP_201_CREATED)
async def add_record(
    record: FormationRecordModel, session: AsyncSession = Depends(get_session)
):
    return await add_formation_record(record, session)


@router.delete("/records/delete", status_code=status.HTTP_200_OK)
async def delete_record(
    record: FormationRecordModel, session: AsyncSession = Depends(get_session)
):
    return await delete_formation_record(record, session)


@router.patch("/records/update", status_code=status.HTTP_200_OK)
async def update_record(
    old: FormationRecordModel,
    new: FormationRecordModel,
    session: AsyncSession = Depends(get_session),
):
    return await update_formation_record(old, new, session)
