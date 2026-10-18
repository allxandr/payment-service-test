from faststream.rabbit import RabbitBroker, RabbitQueue

from app.settings import settings

PAYMENTS_QUEUE = "payments.new"
PAYMENTS_DLQ = "payments.new.dlq"

broker = RabbitBroker(settings.rabbitmq_url)
payments_queue = RabbitQueue(
    PAYMENTS_QUEUE,
    durable=True,
    arguments={
        "x-dead-letter-exchange": "",
        "x-dead-letter-routing-key": PAYMENTS_DLQ,
    },
)
payments_dlq = RabbitQueue(PAYMENTS_DLQ, durable=True)
