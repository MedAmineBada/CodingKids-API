from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.v1.exceptions import AlreadyExists, NotFoundException
from api.v1.models.payment import PaymentModel, Payment
from api.v1.models.student import Student


async def add_payment(payment_model: PaymentModel, session: AsyncSession):
    payment = await session.get(
        Payment, [payment_model.student_id, payment_model.month, payment_model.year]
    )
    if payment:
        raise AlreadyExists("Student already paid for this month.")

    student = await session.get(Student, payment_model.student_id)
    if not student:
        raise NotFoundException()

    att = Payment.model_validate(payment_model)

    session.add(att)
    await session.commit()
    return {"success": "Payment added successfully."}


async def get_payments(student_id: int, session: AsyncSession):
    stmt = (
        select(Payment)
        .where(Payment.student_id == student_id)
        .order_by(Payment.payment_date.desc())
    )
    res = await session.execute(stmt)
    if not res:
        raise NotFoundException("No payments found for this student.")
    return res.scalars().all()
