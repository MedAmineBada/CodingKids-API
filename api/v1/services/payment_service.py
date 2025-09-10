from typing import List, Dict, Any

from sqlmodel import select, extract
from sqlmodel.ext.asyncio.session import AsyncSession

from api.v1.exceptions import AlreadyExists, NotFoundException
from api.v1.models.attendance import Attendance
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


async def get_payment_status(student_id: int, session: AsyncSession):
    """
    Return a list of dicts: { month, year, amount, payment_date, paid }
    where `paid` is True if there's at least one payment for that month/year.
    """
    # get attendance in (month,year) pairs
    att_stmt = (
        select(
            extract("month", Attendance.attend_date).label("month"),
            extract("year", Attendance.attend_date).label("year"),
        )
        .where(Attendance.student_id == student_id)
        .group_by(
            extract("month", Attendance.attend_date),
            extract("year", Attendance.attend_date),
        )
    )
    att_result = await session.execute(att_stmt)
    att_rows = att_result.mappings().all()  # list of dicts {'month': ..., 'year': ...}
    attendance_set = {(int(r["month"]), int(r["year"])) for r in att_rows}

    # get all payments for the student
    pay_stmt = select(
        Payment.month.label("month"),
        Payment.year.label("year"),
        Payment.payment_date.label("payment_date"),
        Payment.amount.label("amount"),
    ).where(Payment.student_id == student_id)
    pay_result = await session.execute(pay_stmt)
    pay_rows = pay_result.mappings().all()

    # aggregate payments by (month, year)
    payment_map: Dict[Tuple[int, int], Dict[str, Any]] = {}
    for r in pay_rows:
        key = (int(r["month"]), int(r["year"]))
        amt = r["amount"] or 0
        pdate = r["payment_date"]

        if key in payment_map:
            # sum amounts
            payment_map[key]["amount"] += amt
            # keep latest payment_date
            if pdate and (
                payment_map[key]["payment_date"] is None
                or pdate > payment_map[key]["payment_date"]
            ):
                payment_map[key]["payment_date"] = pdate
        else:
            payment_map[key] = {"amount": amt, "payment_date": pdate}

    # union attendance months and payment months, and build result rows
    all_keys = attendance_set | set(payment_map.keys())

    # sort ascending by year then month
    sorted_keys = sorted(all_keys, key=lambda ky: (ky[1], ky[0]))

    results: List[Dict[str, Any]] = []
    for month, year in sorted_keys:
        pay = payment_map.get((month, year))
        results.append(
            {
                "month": month,
                "year": year,
                "amount": pay["amount"] if pay else None,
                "payment_date": pay["payment_date"] if pay else None,
                "paid": bool(pay),
            }
        )

    return results
