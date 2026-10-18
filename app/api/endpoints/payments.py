from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException

from app.deps import get_service
from app.schemas.payment import PaymentRequest, PaymentResponse
from app.services.payment import PaymentService

router = APIRouter()


@router.post("/payments", response_model=PaymentResponse)
async def create_payment(
    payment: PaymentRequest,
    idempotency_key: Annotated[str, Header(min_length=1, max_length=255)],
    service: PaymentService = Depends(get_service),
) -> PaymentResponse:
    return await service.create(payment, idempotency_key)


@router.get("/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    service: PaymentService = Depends(get_service),
) -> PaymentResponse:
    payment = await service.get(payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment
