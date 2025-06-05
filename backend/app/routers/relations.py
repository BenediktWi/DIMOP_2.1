from fastapi import APIRouter, Depends, HTTPException
from neo4j import AsyncSession, exceptions

from .websocket import broadcast
from ..database import get_session
from ..models.schemas import Relation, RelationCreate

router = APIRouter(prefix="/relations", tags=["relations"])


@router.post("/", response_model=Relation)
async def create_relation(rel: RelationCreate, session: AsyncSession = Depends(get_session)):
    query = (
        """MATCH (s:Node) WHERE id(s)=$sid MATCH (t:Node) WHERE id(t)=$tid """
        "CREATE (s)-[r:LINK]->(t) RETURN id(r) AS id"
    )
    try:
        result = await session.run(query, sid=rel.source_id, tid=rel.target_id)
    except exceptions.ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Neo4j unavailable")
    record = await result.single()
    await broadcast(rel.project_id, {"op": "create_relation", "id": record["id"], "source": rel.source_id, "target": rel.target_id})
    return Relation(id=record["id"], **rel.model_dump())


@router.delete("/{relation_id}")
async def delete_relation(relation_id: int, session: AsyncSession = Depends(get_session)):
    try:
        await session.run("MATCH ()-[r] WHERE id(r)=$id DELETE r", id=relation_id)
    except exceptions.ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Neo4j unavailable")
    await broadcast(0, {"op": "delete_relation", "id": relation_id})
    return {"ok": True}
