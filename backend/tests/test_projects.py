from fastapi.testclient import TestClient

from app import app
from app.database import get_session


class FakeResult:
    def __init__(self, record):
        self._record = record

    async def single(self):
        return self._record


class FakeSession:
    async def run(self, query, **params):
        return FakeResult({"id": 1, "name": params["name"]})


async def override_get_session():
    yield FakeSession()


def test_create_project():
    app.dependency_overrides[get_session] = override_get_session
    client = TestClient(app)
    response = client.post("/projects/", json={"name": "Demo"})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Demo"}
    app.dependency_overrides.clear()
