from pydantic import BaseModel


class PaymentRequested(BaseModel):
    payment_id: int
