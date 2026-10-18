from app.deps.session import Session
from app.repo.outbox import OutboxRepo
from app.repo.payment import PaymentRepo


def get_payment_repo(session: Session) -> PaymentRepo:
    return PaymentRepo(session)


def get_outbox_repo(session: Session) -> OutboxRepo:
    return OutboxRepo(session)
