from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from .websocket import broadcast
from ..database import get_session, get_write_session
from ..models.schemas import Node, NodeCreate, ConnectionType
from ..models.db import Node as NodeModel

router = APIRouter(prefix="/nodes", tags=["nodes"])


@router.post("/", response_model=Node)
async def create_node(
    node: NodeCreate,
    session: AsyncSession = Depends(get_write_session),
):
    if node.parent_id is not None:
        res = await session.execute(
            select(NodeModel.id).where(
                NodeModel.id == node.parent_id,
                NodeModel.project_id == node.project_id,
            )
        )
        if res.scalar_one_or_none() is None:
            raise HTTPException(status_code=404, detail="Parent node not found")

    ctype_db = node.connection_type
    if isinstance(ctype_db, ConnectionType):
        ctype_db_val = int(ctype_db)
        ctype_resp = ctype_db.name
    elif isinstance(ctype_db, str) and ctype_db.upper() in ConnectionType.__members__:
        ctype_db_val = int(ConnectionType[ctype_db.upper()])
        ctype_resp = ctype_db.upper()
    else:
        ctype_db_val = ctype_db
        ctype_resp = ctype_db

    db_obj = NodeModel(
        project_id=node.project_id,
        material_id=node.material_id,
        name=node.name,
        parent_id=node.parent_id,
        atomic=node.atomic,
        reusable=node.reusable,
        connection_type=ctype_db_val,
        level=node.level,
        weight=node.weight if node.atomic else None,
        recyclable=node.recyclable,
    )
    session.add(db_obj)
    try:
        await session.commit()
        await session.refresh(db_obj)
    except SQLAlchemyError as exc:
        await session.rollback()
        raise HTTPException(status_code=500, detail="DB error") from exc

    node_data = {
        "id": db_obj.id,
        "project_id": node.project_id,
        "material_id": node.material_id,
        "name": node.name,
        "parent_id": node.parent_id,
        "atomic": node.atomic,
        "reusable": node.reusable,
        "connection_type": ctype_resp,
        "level": node.level,
        "weight": node.weight if node.atomic else None,
        "recyclable": node.recyclable,
    }

    await broadcast(node.project_id, {"op": "create_node", "node": node_data})
    return Node(**node_data)


@router.get("/{node_id}", response_model=Node)
async def get_node(
    node_id: int,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(NodeModel).where(NodeModel.id == node_id))
    db_obj = result.scalar_one_or_none()
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Node not found")
    ctype_val = db_obj.connection_type
    ctype_resp = None
    if isinstance(ctype_val, int):
        try:
            ctype_resp = ConnectionType(ctype_val).name
        except ValueError:
            ctype_resp = str(ctype_val)
    return Node(
        id=db_obj.id,
        project_id=db_obj.project_id,
        material_id=db_obj.material_id,
        name=db_obj.name,
        parent_id=db_obj.parent_id,
        atomic=db_obj.atomic,
        reusable=db_obj.reusable,
        connection_type=ctype_resp,
        level=db_obj.level,
        weight=db_obj.weight,
        recyclable=db_obj.recyclable,
    )


@router.delete("/{node_id}")
async def delete_node(
    node_id: int,
    session: AsyncSession = Depends(get_write_session),
):
    res = await session.execute(select(NodeModel).where(NodeModel.id == node_id))
    db_obj = res.scalar_one_or_none()
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Node not found")
    pid = db_obj.project_id
    await session.delete(db_obj)
    await session.commit()
    await broadcast(pid, {"op": "delete_node", "id": node_id})
    return {"ok": True}

