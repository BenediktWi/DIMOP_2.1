from fastapi import APIRouter, Depends, HTTPException
from neo4j import AsyncSession, exceptions

from .websocket import broadcast
from ..database import get_session, get_write_session
from ..models.schemas import Project, ProjectCreate

router = APIRouter(prefix="/projects", tags=["projects"])


# ---------------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------------

@router.post("/", response_model=Project)
async def create_project(
    project: ProjectCreate,
    session: AsyncSession = Depends(get_write_session),
):
    query = (
        "CREATE (p:Project {name: $name}) "
        "RETURN id(p) AS id, p.name AS name"
    )
    try:
        result = await session.run(query, name=project.name)
    except exceptions.ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Neo4j unavailable")

    record = await result.single()
    if record is None:
        raise HTTPException(status_code=404, detail="Resource not found")

    await broadcast(record["id"], {"op": "create_project", "id": record["id"]})
    return Project(id=record["id"], name=record["name"])


# ---------------------------------------------------------------------------
# READ
# ---------------------------------------------------------------------------

@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: int,
    session: AsyncSession = Depends(get_session),
):
    query = (
        "MATCH (p:Project) WHERE id(p)=$id "
        "RETURN id(p) AS id, p.name AS name"
    )
    try:
        result = await session.run(query, id=project_id)
    except exceptions.ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Neo4j unavailable")

    record = await result.single()
    if record is None:
        raise HTTPException(status_code=404, detail="Project not found")

    return Project(id=record["id"], name=record["name"])


# ---------------------------------------------------------------------------
# GRAPH
# ---------------------------------------------------------------------------

@router.get("/{project_id}/graph")
async def get_graph(
    project_id: int,
    session: AsyncSession = Depends(get_session),
):
    # 1) Nodes
    q_nodes = (
        "MATCH (p:Project)<-[:PART_OF]-(n:Node)-[:USES]->(m:Material) "
        "WHERE id(p)=$pid "
        "RETURN id(n) AS id, "
        "       id(m) AS material_id, "
        "       n.name AS name, "
        "       n.parent_id AS parent_id, "
        "       n.atomic AS atomic, "
        "       n.reusable AS reusable, "
        "       n.connection_type AS connection_type, "
        "       n.level AS level, "
        "       n.weight AS weight, "
        "       n.recyclable AS recyclable, "
        "       n.sustainability_score AS sustainability_score"
    )
    try:
        result = await session.run(q_nodes, pid=project_id)
    except exceptions.ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Neo4j unavailable")
    nodes = await result.data()

    # 2) Edges
    q_edges = (
        "MATCH (p:Project)<-[:PART_OF]-(s:Node)-[r:LINK]->(t:Node) "
        "WHERE id(p)=$pid "
        "RETURN id(r) AS id, id(s) AS source, id(t) AS target"
    )
    try:
        res_e = await session.run(q_edges, pid=project_id)
    except exceptions.ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Neo4j unavailable")
    edges = await res_e.data()

    # 3) Materials
    q_mats = (
        "MATCH (m:Material) "
        "RETURN id(m) AS id, "
        "       m.name AS name, "
        "       m.weight AS weight, "
        "       m.co2_value AS co2_value, "
        "       m.hardness AS hardness"
    )
    try:
        res_m = await session.run(q_mats)
    except exceptions.ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Neo4j unavailable")
    materials = await res_m.data()

    # ---------------------------------------------------------------------
    # Aggregate weights for non-atomic nodes (recursive, detects cycles)
    # ---------------------------------------------------------------------
    node_map = {n["id"]: n for n in nodes}

    def calc_weight(nid: int, visited: set[int]) -> float:
        if nid in visited:
            raise HTTPException(status_code=400, detail="Cycle detected")

        visited.add(nid)
        node = node_map[nid]

        # Atomic nodes already carry their own weight
        if node.get("atomic"):
            visited.remove(nid)
            return node.get("weight", 0.0)

        # Sum children weights
        total = 0.0
        for child in nodes:
            if child.get("parent_id") == nid:
                total += calc_weight(child["id"], visited)

        node["weight"] = total
        visited.remove(nid)
        return total

    for n in nodes:
        if not n.get("atomic"):
            calc_weight(n["id"], set())

    return {"nodes": nodes, "edges": edges, "materials": materials}
