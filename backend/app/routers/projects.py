from fastapi import APIRouter, Depends, HTTPException
from neo4j import AsyncSession, exceptions

from .websocket import broadcast
from ..database import get_session
from ..models.schemas import Project, ProjectCreate

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=Project)
async def create_project(project: ProjectCreate, session: AsyncSession = Depends(get_session)):
    query = """CREATE (p:Project {name: $name}) RETURN id(p) AS id, p.name AS name"""
    try:
        result = await session.run(query, name=project.name)
    except exceptions.ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Neo4j unavailable")
    record = await result.single()
    if not record:
        raise HTTPException(status_code=404, detail="Resource not found")
    await broadcast(record["id"], {"op": "create_project", "id": record["id"]})
    return Project(id=record["id"], name=record["name"])


@router.get("/{project_id}", response_model=Project)
async def get_project(project_id: int, session: AsyncSession = Depends(get_session)):
    query = "MATCH (p:Project) WHERE id(p)=$id RETURN id(p) AS id, p.name AS name"
    try:
        result = await session.run(query, id=project_id)
    except exceptions.ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Neo4j unavailable")
    record = await result.single()
    if not record:
        raise HTTPException(status_code=404, detail="Project not found")
    return Project(id=record["id"], name=record["name"])


@router.get("/{project_id}/graph")
async def get_graph(project_id: int, session: AsyncSession = Depends(get_session)):
    q_nodes = "MATCH (p:Project)<-[:PART_OF]-(n:Node)-[:USES]->(m:Material) WHERE id(p)=$pid RETURN id(n) AS id, id(m) AS material_id, n.level AS level"
    try:
        result = await session.run(q_nodes, pid=project_id)
    except exceptions.ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Neo4j unavailable")
    nodes = [dict(record) for record in await result.to_list()]
    q_edges = "MATCH (p:Project)<-[:PART_OF]-(s:Node)-[r:LINK]->(t:Node) WHERE id(p)=$pid RETURN id(r) AS id, id(s) AS source, id(t) AS target"
    try:
        res_e = await session.run(q_edges, pid=project_id)
    except exceptions.ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Neo4j unavailable")
    edges = [dict(record) for record in await res_e.to_list()]
    q_mats = "MATCH (m:Material) RETURN id(m) AS id, m.name AS name, m.weight AS weight"
    try:
        res_m = await session.run(q_mats)
    except exceptions.ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Neo4j unavailable")
    materials = [dict(record) for record in await res_m.to_list()]
    return {"nodes": nodes, "edges": edges, "materials": materials}
