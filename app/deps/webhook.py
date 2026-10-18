from collections.abc import AsyncIterator

import aiohttp
from faststream import Depends

from app.services.webhook import WebhookSender


async def get_http_session() -> AsyncIterator[aiohttp.ClientSession]:
    async with aiohttp.ClientSession() as session:
        yield session


def get_webhook_sender(
    session: aiohttp.ClientSession = Depends(get_http_session),
) -> WebhookSender:
    return WebhookSender(session)
