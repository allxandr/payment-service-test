import asyncio
import contextlib

from faststream import Context, ContextRepo, FastStream

import app.messaging.consumer  # noqa: F401
from app.messaging.broker import broker, payments_dlq
from app.messaging.outbox import relay_outbox

app = FastStream(broker)


@app.after_startup
async def declare_dead_letter_queue() -> None:
    await broker.declare_queue(payments_dlq)


@app.after_startup
async def start_outbox_relay(context: ContextRepo) -> None:
    context.set_global("outbox_relay", asyncio.create_task(relay_outbox()))


@app.on_shutdown
async def stop_outbox_relay(outbox_relay: asyncio.Task[None] = Context()) -> None:
    outbox_relay.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await outbox_relay
