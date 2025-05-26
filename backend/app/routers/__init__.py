from . import websocket
from .projects import router as projects_router
from .materials import router as materials_router
from .nodes import router as nodes_router
from .relations import router as relations_router
from .score import router as score_router

__all__ = [
    "projects_router",
    "materials_router",
    "nodes_router",
    "relations_router",
    "score_router",
    "websocket",
]
