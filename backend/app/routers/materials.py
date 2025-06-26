from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError

from .websocket import broadcast
from ..database import get_session, get_write_session
from ..models.schemas import Material, MaterialCreate
from ..models.db import Material as MaterialModel

router = APIRouter(prefix="/materials", tags=["materials"])


# ---------------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------------

@router.post("/", response_model=Material)
async def create_material(
    material: MaterialCreate,
    session: AsyncSession = Depends(get_write_session),
):
    """Insert a new ``Material`` and return the created object."""
    db_obj = MaterialModel(**material.model_dump())
    session.add(db_obj)
    try:
        await session.commit()
        await session.refresh(db_obj)
    except SQLAlchemyError as exc:
        await session.rollback()
        raise HTTPException(status_code=500, detail="DB error") from exc

    await broadcast(0, {"op": "create_material", "id": db_obj.id})
    return Material.model_validate(db_obj)


# ---------------------------------------------------------------------------
# READ
# ---------------------------------------------------------------------------

@router.get("/{material_id}", response_model=Material)
async def get_material(
    material_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Retrieve a single material by its database ID."""
    result = await session.execute(select(MaterialModel).where(MaterialModel.id == material_id))
    db_obj = result.scalar_one_or_none()
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Material not found")
    return Material.model_validate(db_obj)


# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------

@router.delete("/{material_id}")
async def delete_material(
    material_id: int,
    session: AsyncSession = Depends(get_write_session),
):
    """Remove a material by its ID."""
    result = await session.execute(select(MaterialModel).where(MaterialModel.id == material_id))
    db_obj = result.scalar_one_or_none()
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Material not found")
    await session.delete(db_obj)
    await session.commit()
    await broadcast(0, {"op": "delete_material", "id": material_id})
    return {"ok": True}
