from fastapi import APIRouter, Depends, HTTPException
from neo4j import AsyncSession, exceptions

from ..database import get_session

router = APIRouter(tags=["score"])


@router.post("/score/{project_id}")
async def score_project(project_id: int, session: AsyncSession = Depends(get_session)):
    query = (
        "MATCH (p:Project)<-[:PART_OF]-(n:Node)-[:USES]->(m:Material) "
        "WHERE id(p)=$pid RETURN sum(m.weight) AS total"
    )
    try:
        result = await session.run(query, pid=project_id)
    except exceptions.ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Neo4j unavailable")
    record = await result.single()
    total = record["total"] or 0
    normalized = min(total / 1000.0, 1)
    return 1 - normalized
