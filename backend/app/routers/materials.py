from fastapi import APIRouter, Depends, HTTPException
from neo4j import AsyncSession, exceptions

from .websocket import broadcast
from ..database import get_session, get_write_session
from ..models.schemas import Material, MaterialCreate

router = APIRouter(prefix="/materials", tags=["materials"])


@router.post("/", response_model=Material)
async def create_material(
    material: MaterialCreate,
    session: AsyncSession = Depends(get_write_session),
):
    query = (
        "CREATE (m:Material {name: $name, weight: $weight}) "
        "RETURN id(m) AS id, m.name AS name, m.weight AS weight"
    )
    try:
        result = await session.run(
            query,
            name=material.name,
            weight=material.weight,
        )
    except exceptions.ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Neo4j unavailable")
    record = await result.single()
    if not record:
        raise HTTPException(status_code=404, detail="Resource not found")
    await broadcast(0, {"op": "create_material", "id": record["id"]})
    return Material(
        id=record["id"],
        name=record["name"],
        weight=record["weight"],
    )


@router.get("/{material_id}", response_model=Material)
async def get_material(
    material_id: int,
    session: AsyncSession = Depends(get_session),
):
    query = (
        "MATCH (m:Material) WHERE id(m)=$id "
        "RETURN id(m) AS id, m.name AS name, m.weight AS weight"
    )
    try:
        result = await session.run(query, id=material_id)
    except exceptions.ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Neo4j unavailable")
    record = await result.single()
    if not record:
        raise HTTPException(status_code=404, detail="Material not found")
    return Material(
        id=record["id"],
        name=record["name"],
        weight=record["weight"],
    )


@router.delete("/{material_id}")
async def delete_material(
    material_id: int,
    session: AsyncSession = Depends(get_write_session),
):
    try:
        await session.run(
            "MATCH (m:Material) WHERE id(m)=$id DETACH DELETE m",
            id=material_id,
        )
    except exceptions.ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Neo4j unavailable")
    await broadcast(0, {"op": "delete_material", "id": material_id})
    return {"ok": True}
