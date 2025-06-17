from __future__ import annotations

import httpx


async def create_node(
    http_client: httpx.AsyncClient,
    project_id: int,
    material_id: int,
    level: int,
    parent_id: int | None = None,
) -> dict:
    """Create a node via ``POST /nodes/``.

    Parameters
    ----------
    http_client:
        An initialized ``httpx.AsyncClient`` to use for the request.
    project_id:
        ID of the project the node belongs to.
    material_id:
        ID of the material the node uses.
    level:
        Tree level of the node. ``0`` represents the root level.
    parent_id:
        ID of the parent node or ``None`` for root nodes.

    Returns
    -------
    dict
        The JSON response from the backend.

    Raises
    ------
    ValueError
        If ``level`` and ``parent_id`` do not satisfy the backend constraints.
    httpx.HTTPStatusError
        If the backend returns an error response (status >= 400).
    """
    if level == 0 and parent_id is not None:
        raise ValueError("level 0 nodes cannot have a parent")
    if level > 0 and parent_id is None:
        raise ValueError("non-root nodes must define parent_id")

    payload = {
        "project_id": project_id,
        "material_id": material_id,
        "level": level,
        "parent_id": parent_id,
    }
    response = await http_client.post("/nodes/", json=payload)
    response.raise_for_status()
    return response.json()
