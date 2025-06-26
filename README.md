# Circular Design Toolkit

This repository contains a minimal FastAPI backend and a React\+Vite frontend used to model material flows.
The frontend relies on **ReactFlow v11** for the graph editor. Components using ReactFlow must import `reactflow/dist/style.css` to include its default styles.

## Requirements

- Python 3.11 or newer
- Node.js 18 or newer
- SQLite is used for persistence (no external database required)

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

### Create a project

The frontend can load any project ID. Create a project via the API:

```bash
curl -X POST http://localhost:8000/projects/ \
  -H 'Content-Type: application/json' \
  -d '{"name": "My Project"}'
```

Note the trailing slash in `/projects/`. Omitting it triggers a redirect that
causes a `405 Method Not Allowed` error.

Once created, note the numeric ID from the response. Specify this ID in the
frontend by appending `?project=<id>` to the URL or by storing it in the
browser's local storage under the key `projectId`. Visiting for example
`http://localhost:5173/?project=2` will persist the ID `2` and load that
project on subsequent visits.

### Configuration

Set the ``DATABASE_URL`` environment variable to change the SQLite database location. The default is ``sqlite+aiosqlite:///./backend/app.db``.

### Building for production

To create a production build of the frontend use:

```bash
npm run build
```

The built files can then be served by any static file server or integrated into the backend.

## Repository layout

- `backend/` – FastAPI application
- `frontend/` – React client using Vite and Tailwind CSS

## License

This project is licensed under the [MIT License](LICENSE).
