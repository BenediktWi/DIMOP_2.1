# Backend Setup

This backend uses **FastAPI** with SQLAlchemy and SQLite. Install dependencies via pip:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The application stores its data in the file `app.db` in the backend directory. Set `DATABASE_URL` to use a different location.

During startup the app verifies the database connection. Set the environment variable `TESTING=1` to skip this check (used by the test suite).

The `pyproject.toml` file is kept only for reference and is not used by these instructions.


## Running tests

The `tests/` directory contains pytest-based tests. They run against an in-memory SQLite database. Install the dependencies and run the tests from within `backend`:

```bash
cd backend
pip install -r requirements.txt
pytest
```
