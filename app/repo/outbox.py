from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.outbox import OutboxMessage


class OutboxRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, payment_id: int) -> None:
        statement = (
            insert(OutboxMessage)
            .values(payment_id=payment_id)
            .on_conflict_do_nothing(index_elements=[OutboxMessage.payment_id])
        )
        await self._session.execute(statement)

    async def claim_next(self) -> OutboxMessage | None:
        statement = (
            select(OutboxMessage)
            .where(OutboxMessage.published_at.is_(None))
            .order_by(OutboxMessage.payment_id)
            .limit(1)
            .with_for_update(skip_locked=True)
        )
        return await self._session.scalar(statement)
