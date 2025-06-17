from fastapi import APIRouter, Depends, HTTPException
from neo4j import AsyncSession, exceptions

from ..database import get_write_session
from ..models.schemas import NodeScore

router = APIRouter(tags=["score"])


@router.post("/score/{project_id}", response_model=list[NodeScore])
async def score_project(
    project_id: int,
    session: AsyncSession = Depends(get_write_session),
):
    query = (
        "MATCH (p:Project)<-[:PART_OF]-(n:Node)-[:USES]->(m:Material) "
        "WHERE id(p)=$pid RETURN id(n) AS nid, m.co2_value AS co2, "
        "n.weight AS weight, n.connection_type AS ctype, n.reusable AS reusable"
    )
    try:
        result = await session.run(query, pid=project_id)
    except exceptions.ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Neo4j unavailable")
    records = await result.data()

    def factor(ctype: str | int | None) -> float:
        mapping = {0: "screw", 1: "bolt", 2: "glue"}
        if isinstance(ctype, int):
            ctype = mapping.get(ctype)
        return {"screw": 0.8, "bolt": 1.0, "glue": 1.2}.get(ctype or "", 1.0)

    scores: list[NodeScore] = []
    for rec in records:
        weight = rec.get("weight") or 0.0
        score = (
            (rec.get("co2") or 0.0)
            * weight
            * factor(rec.get("ctype"))
            * (0.5 if rec.get("reusable") else 1.0)
        )
        await session.run(
            "MATCH (n:Node) WHERE id(n)=$id SET n.sustainability_score=$score",
            id=rec["nid"],
            score=score,
        )
        scores.append(NodeScore(id=rec["nid"], sustainability_score=score))

    return scores
