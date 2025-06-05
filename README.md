# Circular Design Toolkit

This repository contains a minimal FastAPI backend and a React\+Vite frontend used to model material flows.
The frontend relies on **ReactFlow v11** for the graph editor. Components using ReactFlow must import `reactflow/dist/style.css` to include its default styles.

## Requirements

- Python 3.11 or newer
- Node.js 18 or newer
- A running Neo4j instance (defaults to `bolt://localhost:7687` with user `neo4j`/`neo4j`).
  API requests will fail unless Neo4j runs with these credentials or the
  environment variables `NEO4J_URI`, `NEO4J_USER` and `NEO4J_PASSWORD` are set
  accordingly.

## Quick start

### 1. Start the backend

Create and activate a Python virtual environment before installing the
dependencies:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # on Windows use "venv\\Scripts\\activate"
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### 2. Start the frontend

Open another terminal and run:

```bash
cd frontend
npm install
npm run dev
```

With both processes running the application is reachable at [http://localhost:5173](http://localhost:5173) and talks to the API on port 8000.
If the initial API request fails (for example due to a 404 or connection issue),
the frontend shows an error message instead of the editor.

### Create your first project

The frontend currently expects that a project with ID `1` exists. You can create
it via the API using `curl`:

```bash
curl -X POST http://localhost:8000/projects/ \
  -H 'Content-Type: application/json' \
  -d '{"name": "My Project"}'
```

Note the trailing slash in `/projects/`. Omitting it triggers a redirect that
causes a `405 Method Not Allowed` error.

### Configuration

If your Neo4j database is not running locally use the environment variables
`NEO4J_URI`, `NEO4J_USER` and `NEO4J_PASSWORD` to override the defaults;
otherwise all API requests will fail.

### Building for production

To create a production build of the frontend use:

```bash
npm run build
```

The built files can then be served by any static file server or integrated into the backend.

## Repository layout

- `backend/` – FastAPI application
- `frontend/` – React client using Vite and Tailwind CSS
