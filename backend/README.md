# Backend Setup

This backend uses **FastAPI** with the async Neo4j driver. Install dependencies via Poetry:

```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload
```

By default the app expects a local Neo4j instance reachable at `bolt://localhost:7687` with user/password `neo4j`. Set `NEO4J_URI`, `NEO4J_USER`, and `NEO4J_PASSWORD` to override.
