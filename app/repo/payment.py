from sqlalchemy import func, inspect, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Payment, PaymentStatus


class PaymentRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, payment: Payment) -> Payment:
        values = {
            attribute.key: value
            for attribute in inspect(Payment).column_attrs
            if (value := getattr(payment, attribute.key)) is not None
        }
        statement = insert(Payment).values(values)
        statement = statement.on_conflict_do_update(
            index_elements=[Payment.idempotency_key],
            set_={Payment.idempotency_key: statement.excluded.idempotency_key},
        ).returning(Payment)
        return (await self._session.scalars(statement)).one()

    async def get(self, payment_id: int) -> Payment | None:
        return await self._session.get(Payment, payment_id)

    async def claim(self, payment_id: int) -> int | None:
        statement = (
            update(Payment)
            .where(
                Payment.id == payment_id,
                Payment.status == PaymentStatus.PENDING,
            )
            .values(status=PaymentStatus.PROCESSING)
            .returning(Payment.id)
        )
        return await self._session.scalar(statement)

    async def complete(self, payment_id: int, status: PaymentStatus) -> Payment:
        statement = (
            update(Payment)
            .where(
                Payment.id == payment_id,
                Payment.status == PaymentStatus.PROCESSING,
            )
            .values(status=status, processed_at=func.now())
            .returning(Payment)
        )
        return (await self._session.execute(statement)).scalar_one()
