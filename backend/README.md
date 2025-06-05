# Backend Setup

This backend uses **FastAPI** with the async Neo4j driver. Install dependencies via pip:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

By default the app expects a local Neo4j instance reachable at
`bolt://localhost:7687` with user/password `neo4j`.
API requests will fail unless Neo4j runs with these credentials or you set the
environment variables `NEO4J_URI`, `NEO4J_USER` and `NEO4J_PASSWORD` to match
your database. You can copy `.env.example` to `.env` to define them.

The `pyproject.toml` file is kept only for reference and is not used by these instructions.
