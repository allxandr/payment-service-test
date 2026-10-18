from decimal import Decimal

from app.models.payment import Currency, Payment, PaymentStatus
from app.repo.outbox import OutboxRepo
from app.repo.payment import PaymentRepo
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import Executable


class RecordingSession(AsyncSession):
    def __init__(self) -> None:
        super().__init__()
        self.statements: list[Executable] = []

    async def execute(
        self, statement: Executable, params: object = None, **kwargs: object
    ) -> object:
        self.statements.append(statement)

        class Result:
            def scalar_one(self) -> None:
                return None

        return Result()

    async def scalars(
        self, statement: Executable, params: object = None, **kwargs: object
    ) -> object:
        self.statements.append(statement)

        class Result:
            def one(self) -> None:
                return None

        return Result()

    async def scalar(self, statement: Executable, params: object = None, **kwargs: object) -> None:
        self.statements.append(statement)
        return None


def _sql(session: RecordingSession) -> tuple[str, dict[str, object]]:
    compiled = session.statements[-1].compile(dialect=postgresql.dialect())
    return " ".join(str(compiled).split()), compiled.params


def _payment() -> Payment:
    return Payment(
        id=1,
        idempotency_key="order-1",
        amount=Decimal("12.50"),
        currency=Currency.USD,
        description="Invoice",
        meta={"order": "A-1"},
        webhook_url="https://example.com/hook",
        status=PaymentStatus.PENDING,
    )


async def test_payment_create_inserts_on_conflict() -> None:
    session = RecordingSession()
    await PaymentRepo(session).create(_payment())

    sql, params = _sql(session)
    assert sql == (
        "INSERT INTO payments (id, idempotency_key, amount, currency, description, meta, status, "
        "webhook_url) "
        "VALUES (%(id)s::BIGINT, %(idempotency_key)s::VARCHAR, %(amount)s, %(currency)s, "
        "%(description)s::VARCHAR, "
        "%(meta)s::JSONB, %(status)s, %(webhook_url)s::VARCHAR) "
        "ON CONFLICT (idempotency_key) DO UPDATE SET idempotency_key = excluded.idempotency_key "
        "RETURNING payments.id, payments.idempotency_key, payments.amount, payments.currency, "
        "payments.description, payments.meta, payments.status, payments.webhook_url, "
        "payments.created_at, payments.processed_at"
    )
    assert params["idempotency_key"] == "order-1"
    assert params["status"] == PaymentStatus.PENDING
    assert "created_at" not in params


async def test_payment_claim_updates_pending_row() -> None:
    session = RecordingSession()
    await PaymentRepo(session).claim(1)

    sql, params = _sql(session)
    assert sql == (
        "UPDATE payments SET status=%(status)s "
        "WHERE payments.id = %(id_1)s::BIGINT AND payments.status = %(status_1)s "
        "RETURNING payments.id"
    )
    assert params["status"] == PaymentStatus.PROCESSING
    assert params["status_1"] == PaymentStatus.PENDING
    assert params["id_1"] == 1


async def test_payment_complete_sets_processed_at() -> None:
    session = RecordingSession()
    await PaymentRepo(session).complete(1, PaymentStatus.SUCCEEDED)

    sql, params = _sql(session)
    assert sql == (
        "UPDATE payments SET status=%(status)s, processed_at=now() "
        "WHERE payments.id = %(id_1)s::BIGINT AND payments.status = %(status_1)s "
        "RETURNING payments.id, payments.idempotency_key, payments.amount, payments.currency, "
        "payments.description, payments.meta, payments.status, payments.webhook_url, "
        "payments.created_at, payments.processed_at"
    )
    assert params["status"] == PaymentStatus.SUCCEEDED
    assert params["status_1"] == PaymentStatus.PROCESSING


async def test_outbox_create_does_nothing_on_conflict() -> None:
    session = RecordingSession()
    await OutboxRepo(session).create(1)

    sql, params = _sql(session)
    assert sql == (
        "INSERT INTO outbox_messages (payment_id) VALUES (%(payment_id)s::BIGINT) "
        "ON CONFLICT (payment_id) DO NOTHING"
    )
    assert params == {"payment_id": 1}


async def test_outbox_claim_next_locks_the_oldest_unpublished_row() -> None:
    session = RecordingSession()
    await OutboxRepo(session).claim_next()

    sql, params = _sql(session)
    assert sql == (
        "SELECT outbox_messages.payment_id, outbox_messages.created_at, "
        "outbox_messages.published_at FROM outbox_messages "
        "WHERE outbox_messages.published_at IS NULL ORDER BY outbox_messages.payment_id "
        "LIMIT %(param_1)s::INTEGER FOR UPDATE SKIP LOCKED"
    )
    assert params == {"param_1": 1}
