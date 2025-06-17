# Backend Setup

This backend uses **FastAPI** with the async Neo4j driver. Install dependencies via pip:

```bash
cd backend
pip install -r requirements.txt
NEO4J_PASSWORD=your_password uvicorn app.main:app --reload
```

By default the app expects a local Neo4j instance reachable at `bolt://localhost:7687` with user/password `neo4j/your_password`. Set `NEO4J_URI`, `NEO4J_USER`, and `NEO4J_PASSWORD` to override.

During startup the app verifies the database connection. Set the environment variable `TESTING=1` to skip this check (used by the test suite).

The `pyproject.toml` file is kept only for reference and is not used by these instructions.


## Running tests

The `tests/` directory contains pytest-based tests. They use a mocked Neo4j session so no database is required. Install the dependencies and run the tests from within `backend`:

```bash
cd backend
pip install -r requirements.txt
pytest
```

## Creating nodes

When sending a `POST` request to `/nodes/` the backend first verifies that both
the referenced project and material exist. If either lookup fails the endpoint
responds with a `404 Not Found` error.

An example log sequence might look like:

```text
INFO:     127.0.0.1:53439 - "POST /materials/ HTTP/1.1" 200 OK
INFO:     127.0.0.1:53443 - "POST /nodes/ HTTP/1.1" 404 Not Found
```

The second line shows that the node creation failed because the project or
material was not found. Ensure that `project_id` and `material_id` in the
request body refer to existing records before calling this endpoint.
