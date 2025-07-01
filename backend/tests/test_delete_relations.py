import asyncio
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

os.environ["TESTING"] = "1"

from app import app as fastapi_app  # noqa: E402
from app.database import get_session, get_write_session  # noqa: E402
from app.models.db import Base  # noqa: E402


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


def test_relations_removed_on_node_delete(client):
    client.post("/projects/", json={"name": "Demo"})
    client.post(
        "/materials/",
        json={"name": "Steel", "weight": 1.0, "co2_value": 1.0, "hardness": 1.0},
    )
    # node A
    client.post(
        "/nodes/",
        json={
            "project_id": 1,
            "material_id": 1,
            "name": "A",
            "parent_id": None,
            "atomic": True,
            "reusable": False,
            "connection_type": 0,
            "level": 0,
            "weight": 1.0,
            "recyclable": True,
        },
    )
    # node B
    client.post(
        "/nodes/",
        json={
            "project_id": 1,
            "material_id": 1,
            "name": "B",
            "parent_id": None,
            "atomic": True,
            "reusable": False,
            "connection_type": 0,
            "level": 0,
            "weight": 1.0,
            "recyclable": True,
        },
    )
    client.post(
        "/relations/",
        json={"project_id": 1, "source_id": 1, "target_id": 2},
    )

    graph = client.get("/projects/1/graph").json()
    assert {"id": 1, "source": 1, "target": 2} in graph["edges"]

    client.delete("/nodes/2")

    graph = client.get("/projects/1/graph").json()
    assert {"id": 1, "source": 1, "target": 2} not in graph["edges"]
