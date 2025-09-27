"""
Formation route definition module.

All routes that are associated with formations are here.
"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.v1.models.formation import FormationModel, Formation
from api.v1.services.formation_services import (
    add_formation,
    get_formations,
    delete_formation,
    rename_formation,
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
