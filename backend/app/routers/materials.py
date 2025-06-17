from fastapi import APIRouter, Depends, HTTPException
from neo4j import AsyncSession, exceptions

from .websocket import broadcast
from ..database import get_session, get_write_session
from ..models.schemas import Material, MaterialCreate

router = APIRouter(prefix="/materials", tags=["materials"])


# ---------------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------------

@router.post("/", response_model=Material)
async def create_material(
    material: MaterialCreate,
    session: AsyncSession = Depends(get_write_session),
):
    """
    Insert a new `Material` node and return the created object.
    """
    query = (
        "CREATE (m:Material {"
        "  name: $name, "
        "  weight: $weight, "
        "  co2_value: $co2_value, "
        "  hardness: $hardness"
        "}) "
        "RETURN id(m) AS id, "
        "       m.name AS name, "
        "       m.weight AS weight, "
        "       m.co2_value AS co2_value, "
        "       m.hardness AS hardness"
    )
    try:
        result = await session.run(
            query,
            name=material.name,
            weight=material.weight,
            co2_value=material.co2_value,
            hardness=material.hardness,
        )
    except exceptions.ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Neo4j unavailable")

    record = await result.single()
    if record is None:
        raise HTTPException(status_code=404, detail="Resource not found")

    # Notify any live WebSocket clients
    await broadcast(0, {"op": "create_material", "id": record["id"]})

    return Material(
        id=record["id"],
        name=record["name"],
        weight=record["weight"],
        co2_value=record["co2_value"],
        hardness=record["hardness"],
    )


# ---------------------------------------------------------------------------
# READ
# ---------------------------------------------------------------------------

@router.get("/{material_id}", response_model=Material)
async def get_material(
    material_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Retrieve a single material by its database ID.
    """
    query = (
        "MATCH (m:Material) WHERE id(m) = $id "
        "RETURN id(m) AS id, "
        "       m.name AS name, "
        "       m.weight AS weight, "
        "       m.co2_value AS co2_value, "
        "       m.hardness AS hardness"
    )
    try:
        result = await session.run(query, id=material_id)
    except exceptions.ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Neo4j unavailable")

    record = await result.single()
    if record is None:
        raise HTTPException(status_code=404, detail="Material not found")

    return Material(
        id=record["id"],
        name=record["name"],
        weight=record["weight"],
        co2_value=record["co2_value"],
        hardness=record["hardness"],
    )


# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------

@router.delete("/{material_id}")
async def delete_material(
    material_id: int,
    session: AsyncSession = Depends(get_write_session),
):
    """
    Remove a material (and any attached relationships) by its ID.
    """
    try:
        await session.run(
            "MATCH (m:Material) WHERE id(m) = $id DETACH DELETE m",
            id=material_id,
        )
    except exceptions.ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Neo4j unavailable")

    await broadcast(0, {"op": "delete_material", "id": material_id})
    return {"ok": True}
