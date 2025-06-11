import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import verify_connectivity

from .routers import projects, materials, nodes, relations, score, websocket


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.getenv("TESTING"):
        await verify_connectivity()
    yield


app = FastAPI(title="Circular Design Toolkit", lifespan=lifespan)

app.include_router(projects.router)
app.include_router(materials.router)
app.include_router(nodes.router)
app.include_router(relations.router)
app.include_router(score.router)
app.include_router(websocket.router)
