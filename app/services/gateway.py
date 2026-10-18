import asyncio
import random


class PaymentGateway:
    def __init__(
        self,
        *,
        min_processing_seconds: float = 2,
        max_processing_seconds: float = 5,
        success_rate: float = 0.9,
    ) -> None:
        self._min_processing_seconds = min_processing_seconds
        self._max_processing_seconds = max_processing_seconds
        self._success_rate = success_rate

    async def charge(self, payment_id: int) -> bool:
        await asyncio.sleep(
            random.uniform(self._min_processing_seconds, self._max_processing_seconds)
        )
        return random.random() < self._success_rate


payment_gateway = PaymentGateway()
