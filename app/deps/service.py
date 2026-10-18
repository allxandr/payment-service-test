from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.generator import get_generator
from app.deps.session import get_session
from app.ids.generator import IdGenerator
from app.repo.outbox import OutboxRepo
from app.repo.payment import PaymentRepo
from app.services.payment import PaymentService


def get_service(
    session: AsyncSession = Depends(get_session),
    generator: IdGenerator = Depends(get_generator),
) -> PaymentService:
    return PaymentService(PaymentRepo(session), OutboxRepo(session), generator)
