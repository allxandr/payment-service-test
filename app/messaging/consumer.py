from fast_depends import inject
from faststream import Depends

from app.deps import get_gateway, get_payment_repo, get_webhook_sender
from app.messaging.broker import broker, payments_queue
from app.messaging.messages import PaymentRequested
from app.models.payment import Payment, PaymentStatus
from app.repo.payment import PaymentRepo
from app.schemas.payment import PaymentResponse
from app.services.gateway import PaymentGateway
from app.services.webhook import WebhookSender


@inject
async def claim_payment(
    payment_id: int,
    payments: PaymentRepo = Depends(get_payment_repo),
) -> bool:
    return await payments.claim(payment_id) is not None


@inject(cast_result=False)
async def complete_payment(
    payment_id: int,
    status: PaymentStatus,
    payments: PaymentRepo = Depends(get_payment_repo),
) -> Payment:
    return await payments.complete(payment_id, status)


@inject(cast_result=False)
async def settle_payment(
    payment_id: int,
    gateway: PaymentGateway = Depends(get_gateway),
) -> Payment:
    succeeded = await gateway.charge(payment_id)
    status = PaymentStatus.SUCCEEDED if succeeded else PaymentStatus.FAILED
    return await complete_payment(payment_id, status)


@inject(cast=False)
async def notify_client(
    payment: Payment,
    webhooks: WebhookSender = Depends(get_webhook_sender),
) -> None:
    payload = PaymentResponse.model_validate(payment).model_dump(mode="json")
    await webhooks.send(payment.webhook_url, payload)


@broker.subscriber(payments_queue)
async def process_payment(event: PaymentRequested) -> None:
    if not await claim_payment(event.payment_id):
        return
    payment = await settle_payment(event.payment_id)
    await notify_client(payment)
