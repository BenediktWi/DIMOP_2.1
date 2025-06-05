# Circular Design Toolkit

This repository contains a minimal FastAPI backend and a React\+Vite frontend used to model material flows.

## Requirements

- Python 3.11 or newer
- Node.js 18 or newer
- A running Neo4j instance (defaults to `bolt://localhost:7687` with user `neo4j`/`neo4j`)

## Quick start

### 1. Start the backend

Create and activate a Python virtual environment before installing the
dependencies:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # on Windows use "venv\\Scripts\\activate"
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 2. Start the frontend

Open another terminal and run:

```bash
cd frontend
npm install
npm run dev
```

With both processes running the application is reachable at [http://localhost:5173](http://localhost:5173) and talks to the API on port 8000.

### Configuration

If your Neo4j database is not running locally use the environment variables `NEO4J_URI`, `NEO4J_USER` and `NEO4J_PASSWORD` to override the defaults.

### Building for production

To create a production build of the frontend use:

```bash
npm run build
```

The built files can then be served by any static file server or integrated into the backend.

## Repository layout

- `backend/` – FastAPI application
- `frontend/` – React client using Vite and Tailwind CSS
