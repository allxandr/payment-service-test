from app.ids.generator import IdGenerator
from app.models.payment import Payment, PaymentStatus
from app.repo.outbox import OutboxRepo
from app.repo.payment import PaymentRepo
from app.schemas.payment import PaymentRequest, PaymentResponse


class PaymentService:
    def __init__(self, payments: PaymentRepo, outbox: OutboxRepo, generator: IdGenerator) -> None:
        self._repo = payments
        self._outbox = outbox
        self._generator = generator

    def generate_id(self) -> int:
        return self._generator.generate()

    async def create(self, data: PaymentRequest, idempotency_key: str) -> PaymentResponse:
        payment = await self._repo.create(
            Payment(
                id=self.generate_id(),
                idempotency_key=idempotency_key,
                amount=data.amount,
                currency=data.currency,
                description=data.description,
                meta=data.meta,
                webhook_url=str(data.webhook_url),
                status=PaymentStatus.PENDING,
            )
        )
        await self._outbox.create(payment.id)
        return PaymentResponse.model_validate(payment)

    async def get(self, payment_id: int) -> PaymentResponse | None:
        payment = await self._repo.get(payment_id)
        if payment is None:
            return None
        return PaymentResponse.model_validate(payment)
