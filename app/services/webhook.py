import asyncio
import logging
from typing import Any

import aiohttp

logger = logging.getLogger(__name__)


class WebhookSender:
    def __init__(
        self,
        session: aiohttp.ClientSession,
        *,
        max_attempts: int = 3,
        base_delay_seconds: float = 1,
        timeout_seconds: float = 5,
    ) -> None:
        self._session = session
        self._max_attempts = max_attempts
        self._base_delay_seconds = base_delay_seconds
        self._timeout = aiohttp.ClientTimeout(total=timeout_seconds)

    async def send(self, url: str, payload: dict[str, Any]) -> None:
        for attempt in range(1, self._max_attempts + 1):
            try:
                await self._post(url, payload)
                return
            except aiohttp.ClientError, TimeoutError:
                if attempt == self._max_attempts:
                    raise
                delay = self._base_delay_seconds * 2 ** (attempt - 1)
                logger.warning(
                    "webhook to %s failed on attempt %s of %s, retrying in %ss",
                    url,
                    attempt,
                    self._max_attempts,
                    delay,
                    exc_info=True,
                )
                await asyncio.sleep(delay)

    async def _post(self, url: str, payload: dict[str, Any]) -> None:
        async with self._session.post(url, json=payload, timeout=self._timeout) as response:
            response.raise_for_status()
