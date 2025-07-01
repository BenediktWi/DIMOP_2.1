__all__ = ["broadcast"]
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

connections: dict[int, list[WebSocket]] = {}


async def broadcast(project_id: int, message: dict):
    """Send ``message`` to all sockets for ``project_id``.
    
    The special ID ``0`` broadcasts to every connected client.
    """
    targets = []
    if project_id == 0:
        for lst in connections.values():
            targets.extend(lst)
    else:
        targets = connections.get(project_id, [])

    for ws in targets:
        await ws.send_json(message)


@router.websocket("/socket/projects/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: int):
    await websocket.accept()
    connections.setdefault(project_id, []).append(websocket)
    try:
        while True:
            await websocket.receive_text()  # keep alive
    except WebSocketDisconnect:
        connections[project_id].remove(websocket)
