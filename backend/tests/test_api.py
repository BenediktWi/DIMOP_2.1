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


def test_create_project(client):
    res = client.post("/projects/", json={"name": "Demo"})
    assert res.status_code == 200
    assert res.json() == {"id": 1, "name": "Demo"}


def test_create_material(client):
    res = client.post(
        "/materials/",
        json={"name": "Steel", "weight": 7.8, "co2_value": 1.0, "hardness": 10.0},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == 1
    assert data["name"] == "Steel"


def test_create_node_and_graph(client):
    client.post("/projects/", json={"name": "Demo"})
    client.post(
        "/materials/",
        json={"name": "Steel", "weight": 7.8, "co2_value": 1.0, "hardness": 10.0},
    )
    res = client.post(
        "/nodes/",
        json={
            "project_id": 1,
            "material_id": 1,
            "name": "Part",
            "parent_id": None,
            "atomic": True,
            "reusable": False,
            "connection_type": 1,
            "level": 0,
            "weight": 2.0,
            "recyclable": True,
        },
    )
    assert res.status_code == 200
    graph = client.get("/projects/1/graph").json()
    assert len(graph["nodes"]) == 1
    assert graph["nodes"][0]["name"] == "Part"


def test_score_project(client):
    client.post("/projects/", json={"name": "Demo"})
    client.post(
        "/materials/",
        json={"name": "Steel", "weight": 7.8, "co2_value": 1.0, "hardness": 10.0},
    )
    client.post(
        "/nodes/",
        json={
            "project_id": 1,
            "material_id": 1,
            "name": "Part",
            "parent_id": None,
            "atomic": True,
            "reusable": False,
            "connection_type": 1,
            "level": 0,
            "weight": 2.0,
            "recyclable": True,
        },
    )
    res = client.post("/score/1")
    assert res.status_code == 200
    scores = res.json()
    assert scores[0]["id"] == 1


def test_finalize_project(client):
    client.post("/projects/", json={"name": "Demo"})
    client.post(
        "/materials/",
        json={"name": "Steel", "weight": 1.0, "co2_value": 1.0, "hardness": 1.0},
    )
    # root node, non atomic
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
    # child 1
    client.post(
        "/nodes/",
        json={
            "project_id": 1,
            "material_id": 1,
            "name": "Child1",
            "parent_id": 1,
            "atomic": True,
            "reusable": False,
            "connection_type": 0,
            "level": 1,
            "weight": 2.0,
            "recyclable": True,
        },
    )
    # child 2
    client.post(
        "/nodes/",
        json={
            "project_id": 1,
            "material_id": 1,
            "name": "Child2",
            "parent_id": 1,
            "atomic": True,
            "reusable": False,
            "connection_type": 0,
            "level": 1,
            "weight": 3.0,
            "recyclable": True,
        },
    )

    res = client.post("/projects/1/finalize")
    assert res.status_code == 200
    data = res.json()
    root_node = next(n for n in data if n["id"] == 1)
    assert root_node["weight"] == 5.0


def test_child_level_validation(client):
    client.post("/projects/", json={"name": "Demo"})
    client.post(
        "/materials/",
        json={"name": "Steel", "weight": 1.0, "co2_value": 1.0, "hardness": 1.0},
    )

    # root node
    res = client.post(
        "/nodes/",
        json={
            "project_id": 1,
            "material_id": 1,
            "name": "Root",
            "parent_id": None,
            "atomic": True,
            "reusable": False,
            "connection_type": 0,
            "level": 0,
            "weight": 1.0,
            "recyclable": True,
        },
    )
    assert res.status_code == 200

    # valid child (level 1)
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
            "weight": 1.0,
            "recyclable": True,
        },
    )
    assert res.status_code == 200

    # invalid child (level mismatch)
    res = client.post(
        "/nodes/",
        json={
            "project_id": 1,
            "material_id": 1,
            "name": "BadChild",
            "parent_id": 1,
            "atomic": True,
            "reusable": False,
            "connection_type": 0,
            "level": 2,
            "weight": 1.0,
            "recyclable": True,
        },
    )
    assert res.status_code == 400

