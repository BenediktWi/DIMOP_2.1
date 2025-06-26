import os
os.environ["TESTING"] = "1"

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app import app as fastapi_app
from app.database import get_session, get_write_session
from app.models.db import Base

import pytest


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
    import asyncio
    asyncio.get_event_loop().run_until_complete(init_models())

    with TestClient(fastapi_app) as c:
        yield c

    fastapi_app.dependency_overrides.clear()
    import asyncio
    asyncio.get_event_loop().run_until_complete(engine.dispose())


def test_parent_edge_in_graph(client):
    client.post("/projects/", json={"name": "Demo"})
    client.post(
        "/materials/",
        json={"name": "Steel", "weight": 1.0, "co2_value": 1.0, "hardness": 1.0},
    )
    # root node
    client.post(
        "/nodes/",
        json={
            "project_id": 1,
            "material_id": 1,
            "name": "Root",
            "parent_id": None,
            "atomic": False,
            "reusable": False,
            "connection_type": 0,
            "level": 0,
            "recyclable": True,
        },
    )
    # child node
    res = client.post(
        "/nodes/",
        json={
            "project_id": 1,
            "material_id": 1,
            "name": "Child",
            "parent_id": 1,
            "atomic": True,
            "reusable": False,
            "connection_type": 0,
            "level": 1,
            "weight": 2.0,
            "recyclable": True,
        },
    )
    nid = res.json()["id"]
    graph = client.get("/projects/1/graph").json()
    assert {"id": -nid, "source": 1, "target": nid} in graph["edges"]

