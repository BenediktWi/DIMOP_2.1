from fastapi import FastAPI

from .routers import projects, materials, nodes, relations, score, websocket

app = FastAPI(title="Circular Design Toolkit")

app.include_router(projects.router)
app.include_router(materials.router)
app.include_router(nodes.router)
app.include_router(relations.router)
app.include_router(score.router)
app.include_router(websocket.router)
