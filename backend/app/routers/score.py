from fastapi import APIRouter, Depends, HTTPException
from neo4j import AsyncSession, exceptions

from ..database import get_write_session
from ..models.schemas import NodeScore, ConnectionType

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

    factor_map = {
        ConnectionType.SCREW: 0.8,
        ConnectionType.BOLT: 1.0,
        ConnectionType.GLUE: 1.2,
    }

    def factor(ctype: str | int | ConnectionType | None) -> float:
        if isinstance(ctype, str):
            try:
                ctype = ConnectionType[ctype.upper()]
            except KeyError:
                return 1.0
        else:
            try:
                ctype = ConnectionType(ctype)
            except Exception:
                return 1.0
        return factor_map.get(ctype, 1.0)

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
