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
