import asyncio
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

os.environ["TESTING"] = "1"

from app import app as fastapi_app  # noqa: E402
from app.database import get_session, get_write_session  # noqa: E402
from app.models.db import Base  # noqa: E402
from app.routers.websocket import broadcast  # noqa: E402


@pytest.fixture()
def client():
    database_url = "sqlite+aiosqlite:///:memory:"
    engine = create_async_engine(database_url, future=True)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_session(*, write: bool = False):
        async with SessionLocal() as session:
            yield session

    async def override_get_write_session():
        async for s in override_get_session(write=True):
            yield s

    fastapi_app.dependency_overrides[get_session] = override_get_session
    fastapi_app.dependency_overrides[get_write_session] = override_get_write_session

    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    asyncio.get_event_loop().run_until_complete(init_models())

    with TestClient(fastapi_app) as c:
        yield c

    fastapi_app.dependency_overrides.clear()
    asyncio.get_event_loop().run_until_complete(engine.dispose())


def test_broadcast_all_projects(client):
    with client.websocket_connect("/socket/projects/1") as ws1, client.websocket_connect(
        "/socket/projects/2"
    ) as ws2:
        msg = {"type": "ping"}
        asyncio.get_event_loop().run_until_complete(broadcast(0, msg))
        assert ws1.receive_json() == msg
        assert ws2.receive_json() == msg
