import os

os.environ["TESTING"] = "1"

from fastapi.testclient import TestClient

from app import app
from app.database import get_session, get_write_session


# ---------------------------------------------------------------------------
# Helpers & fake Neo4j sessions
# ---------------------------------------------------------------------------

class FakeResult:
    def __init__(self, record):
        self._record = record

    async def single(self):
        return self._record


class FakeResultList:
    def __init__(self, data_list):
        self._data_list = data_list

    async def data(self):
        return self._data_list


class FakeSession:
    """Write session for project creation."""
    async def run(self, query, **params):
        return FakeResult({"id": 1, "name": params["name"]})


class FakeSessionNode:
    """Write session for node creation."""
    async def run(self, query, **params):
        return FakeResult({"id": 1})


class FakeSessionMaterial:
    """Write session for material creation."""
    async def run(self, query, **params):
        return FakeResult(
            {
                "id": 1,
                "name": params["name"],
                "weight": params["weight"],
                "co2_value": params["co2_value"],
                "hardness": params["hardness"],
            }
        )


class FakeSessionGraph:
    """
    Read-only session that returns:
      • call 1 → nodes
      • call 2 → edges
      • call 3 → materials
    """
    def __init__(self):
        self._calls = 0

    async def run(self, query, **params):
        self._calls += 1
        if self._calls == 1:            # nodes
            return FakeResultList([
                {
                    "id": 1,
                    "material_id": 2,
                    "name": "Parent",
                    "parent_id": None,
                    "atomic": False,
                    "reusable": False,
                    "connection_type": 1,
                    "level": 0,
                    "weight": 1.0,      # matches test expectation
                    "recyclable": True,
                },
                {
                    "id": 2,
                    "material_id": 3,
                    "name": "Child",
                    "parent_id": 1,
                    "atomic": True,
                    "reusable": False,
                    "connection_type": 1,
                    "level": 1,
                    "weight": 1.0,
                    "recyclable": True,
                },
            ])
        elif self._calls == 2:          # edges
            return FakeResultList([{"id": 10, "source": 1, "target": 2}])
        else:                           # materials
            return FakeResultList([
                {
                    "id": 2,
                    "name": "Steel",
                    "weight": 7.8,
                    "co2_value": 1.0,
                    "hardness": 10.0,
                }
            ])


class FakeSessionGraphCycle:
    """Same pattern as above, but returns a graph with a cycle so the endpoint errors."""
    def __init__(self):
        self._calls = 0

    async def run(self, query, **params):
        self._calls += 1
        if self._calls == 1:            # nodes
            return FakeResultList([
                {
                    "id": 1,
                    "material_id": 2,
                    "name": "A",
                    "parent_id": 2,
                    "atomic": False,
                    "reusable": False,
                    "connection_type": 1,
                    "level": 0,
                    "weight": 0.0,
                    "recyclable": True,
                },
                {
                    "id": 2,
                    "material_id": 2,
                    "name": "B",
                    "parent_id": 1,
                    "atomic": False,
                    "reusable": False,
                    "connection_type": 1,
                    "level": 1,
                    "weight": 0.0,
                    "recyclable": True,
                },
            ])
        elif self._calls == 2:          # edges (cycle present)
            return FakeResultList([
                {"id": 10, "source": 1, "target": 2},
                {"id": 11, "source": 2, "target": 1},
            ])
        else:                           # materials
            return FakeResultList([
                {
                    "id": 2,
                    "name": "Steel",
                    "weight": 7.8,
                    "co2_value": 1.0,
                    "hardness": 10.0,
                }
            ])


# ---------------------------------------------------------------------------
# Dependency overrides
# ---------------------------------------------------------------------------

async def override_get_session():
    yield FakeSession()


async def override_get_session_graph():
    yield FakeSessionGraph()


async def override_get_session_graph_cycle():
    yield FakeSessionGraphCycle()


async def override_get_session_node():
    yield FakeSessionNode()


async def override_get_session_material():
    yield FakeSessionMaterial()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

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
        "nodes": [
            {
                "id": 1,
                "material_id": 2,
                "name": "Parent",
                "parent_id": None,
                "atomic": False,
                "reusable": False,
                "connection_type": 1,
                "level": 0,
                "weight": 1.0,
                "recyclable": True,
            },
            {
                "id": 2,
                "material_id": 3,
                "name": "Child",
                "parent_id": 1,
                "atomic": True,
                "reusable": False,
                "connection_type": 1,
                "level": 1,
                "weight": 1.0,
                "recyclable": True,
            },
        ],
        "edges": [{"id": 10, "source": 1, "target": 2}],
        "materials": [
            {
                "id": 2,
                "name": "Steel",
                "weight": 7.8,
                "co2_value": 1.0,
                "hardness": 10.0,
            }
        ],
    }

    app.dependency_overrides.clear()


def test_get_graph_cycle():
    app.dependency_overrides[get_session] = override_get_session_graph_cycle
    client = TestClient(app)

    response = client.get("/projects/1/graph")
    assert response.status_code == 400
    assert response.json() == {"detail": "Cycle detected"}

    app.dependency_overrides.clear()


def test_create_node_atomic():
    app.dependency_overrides[get_write_session] = override_get_session_node
    client = TestClient(app)

    response = client.post(
        "/nodes/",
        json={
            "project_id": 1,
            "material_id": 2,
            "name": "Child",
            "parent_id": None,
            "atomic": True,
            "reusable": False,
            "connection_type": 1,
            "level": 0,
            "weight": 1.0,
            "recyclable": True,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "project_id": 1,
        "material_id": 2,
        "name": "Child",
        "parent_id": None,
        "atomic": True,
        "reusable": False,
        "connection_type": 1,
        "level": 0,
        "weight": 1.0,
        "recyclable": True,
    }

    app.dependency_overrides.clear()


def test_create_node_non_atomic():
    app.dependency_overrides[get_write_session] = override_get_session_node
    client = TestClient(app)
    response = client.post(
        "/nodes/",
        json={
            "project_id": 1,
            "material_id": 2,
            "name": "Group",
            "parent_id": None,
            "atomic": False,
            "reusable": False,
            "connection_type": "bolt",
            "level": 0,
            "recyclable": True,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "project_id": 1,
        "material_id": 2,
        "name": "Group",
        "parent_id": None,
        "atomic": False,
        "reusable": False,
        "connection_type": "bolt",
        "level": 0,
        "weight": None,
        "recyclable": True,
    }
    app.dependency_overrides.clear()


def test_atomic_weight_required():
    app.dependency_overrides[get_write_session] = override_get_session_node
    client = TestClient(app)
    response = client.post(
        "/nodes/",
        json={
            "project_id": 1,
            "material_id": 2,
            "name": "Child",
            "parent_id": None,
            "atomic": True,
            "reusable": False,
            "connection_type": "bolt",
            "level": 0,
            "recyclable": True,
        },
    )
    assert response.status_code == 422
    app.dependency_overrides.clear()


def test_create_material():
    app.dependency_overrides[get_write_session] = override_get_session_material
    client = TestClient(app)
    response = client.post(
        "/materials/",
        json={"name": "Steel", "weight": 7.8, "co2_value": 1.0, "hardness": 10.0},
    )
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "Steel",
        "weight": 7.8,
        "co2_value": 1.0,
        "hardness": 10.0,
    }
    app.dependency_overrides.clear()
