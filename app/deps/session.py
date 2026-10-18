from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends as FastAPIDepends
from faststream import Depends as StreamDepends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import session_scope


async def get_session() -> AsyncIterator[AsyncSession]:
    async with session_scope() as session:
        yield session


Session = Annotated[AsyncSession, FastAPIDepends(get_session), StreamDepends(get_session)]
