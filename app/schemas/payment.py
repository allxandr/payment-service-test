from datetime import datetime
from decimal import Decimal
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, PlainSerializer, WithJsonSchema

from app.models.payment import Currency, PaymentStatus

PaymentId = Annotated[
    int,
    PlainSerializer(str, return_type=str, when_used="json"),
    WithJsonSchema({"type": "string"}),
]


class PaymentRequest(BaseModel):
    amount: Decimal
    currency: Currency
    description: str = Field(max_length=255)
    meta: dict[str, Any] = Field(default_factory=dict)
    webhook_url: HttpUrl = Field(max_length=255)


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PaymentId
    amount: Decimal
    currency: Currency
    description: str
    meta: dict[str, Any]
    status: PaymentStatus
    webhook_url: str
    created_at: datetime
    processed_at: datetime | None
