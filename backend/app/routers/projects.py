from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from .websocket import broadcast
from ..database import get_session, get_write_session
from ..models.schemas import Project, ProjectCreate, ConnectionType, Node
from ..models.db import (
    Project as ProjectModel,
    Node as NodeModel,
    Relation as RelationModel,
    Material as MaterialModel,
)

router = APIRouter(prefix="/projects", tags=["projects"])


# ---------------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------------

@router.post("/", response_model=Project)
async def create_project(
    project: ProjectCreate,
    session: AsyncSession = Depends(get_write_session),
):
    db_obj = ProjectModel(name=project.name)
    session.add(db_obj)
    try:
        await session.commit()
        await session.refresh(db_obj)
    except SQLAlchemyError as exc:
        await session.rollback()
        raise HTTPException(status_code=500, detail="DB error") from exc

    await broadcast(db_obj.id, {"op": "create_project", "id": db_obj.id})
    return Project(id=db_obj.id, name=db_obj.name)


# ---------------------------------------------------------------------------
# READ
# ---------------------------------------------------------------------------

@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: int,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(ProjectModel).where(ProjectModel.id == project_id))
    db_obj = result.scalar_one_or_none()
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return Project(id=db_obj.id, name=db_obj.name)


# ---------------------------------------------------------------------------
# GRAPH
# ---------------------------------------------------------------------------

@router.get("/{project_id}/graph")
async def get_graph(
    project_id: int,
    session: AsyncSession = Depends(get_session),
):
    result_nodes = await session.execute(select(NodeModel).where(NodeModel.project_id == project_id))
    nodes = []
    for db_node in result_nodes.scalars():
        cval = db_node.connection_type
        if isinstance(cval, int):
            try:
                cval = ConnectionType(cval).name
            except ValueError:
                cval = str(cval)
        nodes.append(
            {
                "id": db_node.id,
                "material_id": db_node.material_id,
                "name": db_node.name,
                "parent_id": db_node.parent_id,
                "atomic": db_node.atomic,
                "reusable": db_node.reusable,
                "connection_type": cval,
                "level": db_node.level,
                "weight": db_node.weight,
                "recyclable": db_node.recyclable,
                "sustainability_score": db_node.sustainability_score,
            }
        )

    # 2) Edges
    result_edges = await session.execute(select(RelationModel).where(RelationModel.project_id == project_id))
    edges = [
        {"id": rel.id, "source": rel.source_id, "target": rel.target_id}
        for rel in result_edges.scalars()
    ]

    # 3) Materials
    res_mats = await session.execute(select(MaterialModel))
    materials = [
        {
            "id": m.id,
            "name": m.name,
            "weight": m.weight,
            "co2_value": m.co2_value,
            "hardness": m.hardness,
        }
        for m in res_mats.scalars()
    ]

    # ---------------------------------------------------------------------
    # Aggregate weights for non-atomic nodes (recursive, detects cycles)
    # ---------------------------------------------------------------------
    node_map = {n["id"]: n for n in nodes}

    def calc_weight(nid: int, visited: set[int]) -> float:
        if nid in visited:
            raise HTTPException(status_code=400, detail="Cycle detected")

        visited.add(nid)
        node = node_map[nid]

        # Atomic nodes already carry their own weight
        if node.get("atomic"):
            visited.remove(nid)
            return node.get("weight", 0.0)

        # Sum children weights
        total = 0.0
        for child in nodes:
            if child.get("parent_id") == nid:
                total += calc_weight(child["id"], visited)

        node["weight"] = total
        visited.remove(nid)
        return total

    for n in nodes:
        if not n.get("atomic"):
            calc_weight(n["id"], set())

    return {"nodes": nodes, "edges": edges, "materials": materials}


# ---------------------------------------------------------------------------
# FINALIZE PROJECT
# ---------------------------------------------------------------------------

@router.post("/{project_id}/finalize", response_model=list[Node])
async def finalize_project(
    project_id: int,
    session: AsyncSession = Depends(get_write_session),
):
    result = await session.execute(
        select(NodeModel).where(NodeModel.project_id == project_id)
    )
    nodes = list(result.scalars())
    node_map = {n.id: n for n in nodes}

    def calc_weight(nid: int, visited: set[int]) -> float:
        if nid in visited:
            raise HTTPException(status_code=400, detail="Cycle detected")
        visited.add(nid)
        node = node_map[nid]
        if node.atomic:
            visited.remove(nid)
            return node.weight or 0.0
        total = 0.0
        for child in nodes:
            if child.parent_id == nid:
                total += calc_weight(child.id, visited)
        node.weight = total
        visited.remove(nid)
        return total

    for n in nodes:
        if not n.atomic:
            calc_weight(n.id, set())
        session.add(n)

    try:
        await session.commit()
    except SQLAlchemyError as exc:
        await session.rollback()
        raise HTTPException(status_code=500, detail="DB error") from exc

    await broadcast(project_id, {"op": "finalize"})
    return [Node.model_validate(n) for n in nodes]

