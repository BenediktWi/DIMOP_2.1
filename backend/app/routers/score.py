from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError

from ..database import get_write_session
from ..models.schemas import NodeScore, ConnectionType
from ..models.db import Node as NodeModel, Material as MaterialModel

router = APIRouter(tags=["score"])


@router.post("/score/{project_id}", response_model=list[NodeScore])
async def score_project(
    project_id: int,
    session: AsyncSession = Depends(get_write_session),
):
    join_stmt = (
        select(
            NodeModel.id.label("nid"),
            MaterialModel.co2_value.label("co2"),
            NodeModel.weight.label("weight"),
            NodeModel.connection_type.label("ctype"),
            NodeModel.reusable.label("reusable"),
        )
        .join(MaterialModel, NodeModel.material_id == MaterialModel.id)
        .where(NodeModel.project_id == project_id)
    )

    result = await session.execute(join_stmt)
    records = [dict(row._mapping) for row in result]

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
        try:
            await session.execute(
                update(NodeModel)
                .where(NodeModel.id == rec["nid"])
                .values(sustainability_score=score)
            )
            await session.commit()
        except SQLAlchemyError:
            await session.rollback()
            raise HTTPException(status_code=500, detail="DB error")
        scores.append(NodeScore(id=rec["nid"], sustainability_score=score))

    return scores
