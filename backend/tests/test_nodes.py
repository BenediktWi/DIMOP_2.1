import os
import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import asyncio

from app.models.schemas import NodeCreate
from app import app as fastapi_app
from app.database import get_session, get_write_session
from app.models.db import Base

os.environ["TESTING"] = "1"


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


def test_level_zero_no_parent_ok():
    NodeCreate(
        project_id=1,
        material_id=2,
        level=0,
        name="x",
        atomic=False,
        reusable=False,
        recyclable=False,
    )


def test_level_zero_with_parent_fails():
    with pytest.raises(ValidationError):
        NodeCreate(
            project_id=1,
            material_id=2,
            level=0,
            parent_id=1,
            name="x",
            atomic=False,
            reusable=False,
            recyclable=False,
        )


def test_level_gt_zero_missing_parent_fails():
    with pytest.raises(ValidationError):
        NodeCreate(
            project_id=1,
            material_id=2,
            level=1,
            name="x",
            atomic=False,
            reusable=False,
            recyclable=False,
        )


def test_level_gt_zero_with_parent_ok():
    NodeCreate(
        project_id=1,
        material_id=2,
        level=1,
        parent_id=1,
        name="x",
        atomic=False,
        reusable=False,
        recyclable=False,
    )


def test_parent_one_level_above_ok(client):
    client.post("/projects/", json={"name": "Demo"})
    client.post(
        "/materials/",
        json={"name": "Steel", "weight": 1.0, "co2_value": 1.0, "hardness": 1.0},
    )
    client.post(
        "/nodes/",
        json={
            "project_id": 1,
            "material_id": 1,
            "name": "root",
            "parent_id": None,
            "atomic": False,
            "reusable": False,
            "connection_type": 1,
            "level": 0,
            "recyclable": False,
        },
    )
    res = client.post(
        "/nodes/",
        json={
            "project_id": 1,
            "material_id": 1,
            "name": "child",
            "parent_id": 1,
            "atomic": False,
            "reusable": False,
            "connection_type": 1,
            "level": 1,
            "recyclable": False,
        },
    )
    assert res.status_code == 200


def test_parent_level_mismatch_fails(client):
    client.post("/projects/", json={"name": "Demo"})
    client.post(
        "/materials/",
        json={"name": "Steel", "weight": 1.0, "co2_value": 1.0, "hardness": 1.0},
    )
    client.post(
        "/nodes/",
        json={
            "project_id": 1,
            "material_id": 1,
            "name": "root",
            "parent_id": None,
            "atomic": False,
            "reusable": False,
            "connection_type": 1,
            "level": 0,
            "recyclable": False,
        },
    )
    res = client.post(
        "/nodes/",
        json={
            "project_id": 1,
            "material_id": 1,
            "name": "badchild",
            "parent_id": 1,
            "atomic": False,
            "reusable": False,
            "connection_type": 1,
            "level": 2,
            "recyclable": False,
        },
    )
    assert res.status_code == 400
