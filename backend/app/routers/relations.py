from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from .websocket import broadcast
from ..database import get_write_session
from ..models.schemas import Relation, RelationCreate
from ..models.db import Relation as RelationModel, Node as NodeModel

router = APIRouter(prefix="/relations", tags=["relations"])


@router.post("/", response_model=Relation)
async def create_relation(
    rel: RelationCreate,
    session: AsyncSession = Depends(get_write_session),
):
    res_src = await session.execute(select(NodeModel.id).where(NodeModel.id == rel.source_id))
    if res_src.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Source node not found")
    res_tgt = await session.execute(select(NodeModel.id).where(NodeModel.id == rel.target_id))
    if res_tgt.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Target node not found")

    db_obj = RelationModel(
        project_id=rel.project_id,
        source_id=rel.source_id,
        target_id=rel.target_id,
    )
    session.add(db_obj)
    try:
        await session.commit()
        await session.refresh(db_obj)
    except SQLAlchemyError as exc:
        await session.rollback()
        raise HTTPException(status_code=500, detail="DB error") from exc

    await broadcast(
        rel.project_id,
        {
            "op": "create_relation",
            "id": db_obj.id,
            "source": rel.source_id,
            "target": rel.target_id,
        },
    )
    return Relation(id=db_obj.id, **rel.model_dump())


@router.delete("/{relation_id}")
async def delete_relation(
    relation_id: int,
    session: AsyncSession = Depends(get_write_session),
):
    res = await session.execute(select(RelationModel).where(RelationModel.id == relation_id))
    db_obj = res.scalar_one_or_none()
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Relation not found")
    await session.delete(db_obj)
    await session.commit()
    await broadcast(0, {"op": "delete_relation", "id": relation_id})
    return {"ok": True}

