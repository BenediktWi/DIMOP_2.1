from fastapi import APIRouter, Depends, HTTPException
from neo4j import AsyncSession, exceptions

from .websocket import broadcast
from ..database import get_session
from ..models.schemas import Node, NodeCreate

router = APIRouter(prefix="/nodes", tags=["nodes"])


@router.post("/", response_model=Node)
async def create_node(node: NodeCreate, session: AsyncSession = Depends(get_session)):
    query = (
        """MATCH (p:Project) WHERE id(p)=$pid MATCH (m:Material) WHERE id(m)=$mid """
        "CREATE (n:Node {level: $level})-[:USES]->(m)-[:PART_OF]->(p) RETURN id(n) AS id"
    )
    try:
        result = await session.run(query, pid=node.project_id, mid=node.material_id, level=node.level)
    except exceptions.ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Neo4j unavailable")
    record = await result.single()
    await broadcast(node.project_id, {"op": "create_node", "id": record["id"]})
    return Node(id=record["id"], project_id=node.project_id, material_id=node.material_id, level=node.level)


@router.get("/{node_id}", response_model=Node)
async def get_node(node_id: int, session: AsyncSession = Depends(get_session)):
    query = (
        "MATCH (n:Node)-[:USES]->(m:Material) WHERE id(n)=$id "
        "MATCH (n)-[:PART_OF]->(p:Project) "
        "RETURN id(n) AS id, id(p) AS project_id, id(m) AS material_id, n.level AS level"
    )
    try:
        result = await session.run(query, id=node_id)
    except exceptions.ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Neo4j unavailable")
    record = await result.single()
    if not record:
        raise HTTPException(status_code=404, detail="Node not found")
    return Node(**record.data())


@router.delete("/{node_id}")
async def delete_node(node_id: int, session: AsyncSession = Depends(get_session)):
    try:
        result = await session.run("MATCH (n:Node)-[:PART_OF]->(p) WHERE id(n)=$id RETURN id(p) AS pid", id=node_id)
    except exceptions.ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Neo4j unavailable")
    rec = await result.single()
    pid = rec["pid"] if rec else 0
    try:
        await session.run("MATCH (n:Node) WHERE id(n)=$id DETACH DELETE n", id=node_id)
    except exceptions.ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Neo4j unavailable")
    await broadcast(pid, {"op": "delete_node", "id": node_id})
    return {"ok": True}
