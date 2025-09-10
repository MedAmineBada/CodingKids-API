"""
Payment route definition module.

All routes that are associated with student's payment records are here.
"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.v1.models.payment import PaymentModel, PaymentDates
from api.v1.services.payment_service import (
    add_payment,
    get_payments,
    get_payment_status,
)
from db.session import get_session

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/add", status_code=status.HTTP_201_CREATED)
async def add(payment: PaymentModel, session: AsyncSession = Depends(get_session)):
    return await add_payment(payment, session)


@router.get(
    "/{student_id}",
    response_model=List[PaymentDates],
    status_code=status.HTTP_200_OK,
)
async def get(student_id: int, session: AsyncSession = Depends(get_session)):
    return await get_payments(student_id, session)


@router.get("/status/{student_id}", status_code=status.HTTP_200_OK)
async def get_status(student_id: int, session: AsyncSession = Depends(get_session)):
    return await get_payment_status(student_id, session)
