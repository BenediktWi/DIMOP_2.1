from __future__ import annotations

from __future__ import annotations

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import text

from .models.db import Base


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./app.db")

engine = create_async_engine(DATABASE_URL, future=True, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def verify_connectivity() -> None:
    """Ensure the database is reachable and tables exist."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            await conn.execute(text("SELECT 1"))
    except Exception as exc:
        raise RuntimeError("Unable to connect to database") from exc


async def get_session(*, write: bool = False) -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session."""
    async with async_session() as session:
        yield session


async def get_write_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_session(write=True):
        yield session

