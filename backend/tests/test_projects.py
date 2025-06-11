import os

os.environ["TESTING"] = "1"

from fastapi.testclient import TestClient

from app import app
from app.database import get_session, get_write_session


class FakeResult:
    def __init__(self, record):
        self._record = record

    async def single(self):
        return self._record


class FakeSession:
    async def run(self, query, **params):
        return FakeResult({"id": 1, "name": params["name"]})


class FakeResultList:
    def __init__(self, data_list):
        self._data_list = data_list

    async def data(self):
        return self._data_list


class FakeSessionGraph:
    def __init__(self):
        self._calls = 0

    async def run(self, query, **params):
        self._calls += 1
        if self._calls == 1:
            return FakeResultList([
                {"id": 1, "material_id": 2, "level": 0, "weight": 1.0, "recyclable": True}
            ])
        elif self._calls == 2:
            return FakeResultList([
                {"id": 10, "source": 1, "target": 2}
            ])
        else:
            return FakeResultList([
                {"id": 2, "name": "Steel", "weight": 7.8}
            ])


async def override_get_session():
    yield FakeSession()


async def override_get_session_graph():
    yield FakeSessionGraph()


def test_create_project():
    app.dependency_overrides[get_write_session] = override_get_session
    client = TestClient(app)
    response = client.post("/projects/", json={"name": "Demo"})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Demo"}
    app.dependency_overrides.clear()


def test_get_graph():
    app.dependency_overrides[get_session] = override_get_session_graph
    client = TestClient(app)
    response = client.get("/projects/1/graph")
    assert response.status_code == 200
    assert response.json() == {
        "nodes": [{"id": 1, "material_id": 2, "level": 0, "weight": 1.0, "recyclable": True}],
        "edges": [{"id": 10, "source": 1, "target": 2}],
        "materials": [{"id": 2, "name": "Steel", "weight": 7.8}],
    }
    app.dependency_overrides.clear()
