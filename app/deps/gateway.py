from app.services.gateway import PaymentGateway, payment_gateway


def get_gateway() -> PaymentGateway:
    return payment_gateway
