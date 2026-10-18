import asyncio
import logging
from datetime import UTC, datetime

from fast_depends import inject
from faststream import Depends
from faststream.rabbit import RabbitBroker

from app.deps import get_outbox_repo
from app.messaging.broker import PAYMENTS_QUEUE, broker
from app.messaging.messages import PaymentRequested
from app.repo.outbox import OutboxRepo

logger = logging.getLogger(__name__)
POLL_INTERVAL_SECONDS = 1


@inject(cast=False)
async def publish_next(
    publisher: RabbitBroker = broker,
    outbox: OutboxRepo = Depends(get_outbox_repo),
) -> bool:
    message = await outbox.claim_next()
    if message is None:
        return False
    await publisher.publish(
        PaymentRequested(payment_id=message.payment_id),
        queue=PAYMENTS_QUEUE,
        persist=True,
    )
    message.published_at = datetime.now(UTC)
    return True


async def relay_outbox() -> None:
    while True:
        try:
            if await publish_next():
                continue
        except Exception:
            logger.exception("failed to publish outbox message")
        await asyncio.sleep(POLL_INTERVAL_SECONDS)
