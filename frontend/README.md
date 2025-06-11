# Frontend Setup

This React app uses Vite and Tailwind CSS.
It renders flows using **ReactFlow v11**.
Remember to import `reactflow/dist/style.css` in components that use ReactFlow.

```bash
cd frontend
npm install
npm run dev
```

The development server proxies API requests starting with `/projects`, `/materials`,
`/nodes`, `/relations`, `/score` and `/ws` to `http://localhost:8000`. Make sure
the backend is running on that port before starting the frontend. On start it
connects to the backend at the same host and loads project 1. When this request
fails, the app displays an error message to help with troubleshooting.

## Troubleshooting WebSockets

1. Start the backend on port `8000`. If a Neo4j database isn't running you can
   create a temporary app without the connectivity check:
   ```bash
   python - <<'PY'
   from fastapi import FastAPI
   from app.routers import projects, materials, nodes, relations, score, websocket
   app = FastAPI()
   app.include_router(projects.router)
   app.include_router(materials.router)
   app.include_router(nodes.router)
   app.include_router(relations.router)
   app.include_router(score.router)
   app.include_router(websocket.router)
   import uvicorn; uvicorn.run(app, port=8000)
   PY
   ```
2. Start the dev server and note the port printed in the logs (usually `5173`).
3. Test the WebSocket endpoint via the dev server using a small script:
   ```bash
   python - <<'PY'
   import asyncio, websockets
   async def main():
       uri = 'ws://localhost:5173/ws/projects/1'
       async with websockets.connect(uri) as ws:
           await ws.send('ping')
   asyncio.run(main())
   PY
   ```
   If the connection succeeds the proxy is working and `/ws/projects/1` is reachable.
