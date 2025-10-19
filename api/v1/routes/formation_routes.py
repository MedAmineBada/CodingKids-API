"""
Formation route definition module.

All routes that are associated with formations are here.
"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.v1.models.formation import FormationModel, FormationAssignage
from api.v1.models.formation_type import FormationType, FormationTypeModel
from api.v1.services.formation_services import (
    add_formation,
    get_formations,
    delete_formation,
    update_formation,
    get_formation_types,
    add_formation_type,
    delete_formation_type,
    rename_formation_type,
    unassign_formation,
    assign_formation,
)
from db.session import get_session

router = APIRouter(prefix="/formations")


@router.get("/", status_code=status.HTTP_200_OK)
async def get(session: AsyncSession = Depends(get_session)):
    return await get_formations(session)


@router.post("/add", status_code=status.HTTP_201_CREATED)
async def add(formation: FormationModel, session: AsyncSession = Depends(get_session)):
    return await add_formation(formation, session)


@router.delete("/delete/{id}", status_code=status.HTTP_200_OK)
async def delete(id: int, session: AsyncSession = Depends(get_session)):
    return await delete_formation(id, session)


@router.patch("/update/{id}", status_code=status.HTTP_200_OK)
async def update(
    id: int, data: FormationModel, session: AsyncSession = Depends(get_session)
):
    return await update_formation(id, data, session)


@router.get(
    "/types", status_code=status.HTTP_200_OK, response_model=List[FormationType]
)
async def get_types(session: AsyncSession = Depends(get_session)):
    return await get_formation_types(session)


@router.post("/types/add", status_code=status.HTTP_201_CREATED)
async def add_types(
    data: FormationTypeModel, session: AsyncSession = Depends(get_session)
):
    return await add_formation_type(data, session)


@router.delete("/types/delete/{id}", status_code=status.HTTP_200_OK)
async def delete_type(id: int, session: AsyncSession = Depends(get_session)):
    return await delete_formation_type(id, session)


@router.patch("/types/rename/{id}", status_code=status.HTTP_200_OK)
async def rename_type(
    id: int, data: FormationTypeModel, session: AsyncSession = Depends(get_session)
):
    return await rename_formation_type(id, data, session)


@router.patch("/unassign/{teacher_id}", status_code=status.HTTP_200_OK)
async def unassign(
    teacher_id: int,
    formation: FormationAssignage,
    session: AsyncSession = Depends(get_session),
):
    return await unassign_formation(teacher_id, formation.formation_id, session)


@router.patch("/assign/{teacher_id}", status_code=status.HTTP_200_OK)
async def assign(
    teacher_id: int,
    formation: FormationAssignage,
    session: AsyncSession = Depends(get_session),
):
    return await assign_formation(teacher_id, formation.formation_id, session)
