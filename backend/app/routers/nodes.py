from fastapi import APIRouter, Depends, HTTPException
from neo4j import AsyncSession, exceptions

from .websocket import broadcast
from ..database import get_session, get_write_session
from ..models.schemas import Node, NodeCreate, ConnectionType

router = APIRouter(prefix="/nodes", tags=["nodes"])


@router.post("/", response_model=Node)
async def create_node(
    node: NodeCreate,
    session: AsyncSession = Depends(get_write_session),
):
    if node.parent_id is not None:
        try:
            check_result = await session.run(
                "MATCH (p:Project)<-[:PART_OF]-(n:Node) "
                "WHERE id(p)=$pid AND id(n)=$nid RETURN id(n) AS id",
                pid=node.project_id,
                nid=node.parent_id,
            )
        except exceptions.ServiceUnavailable:
            raise HTTPException(status_code=503, detail="Neo4j unavailable")
        parent_rec = await check_result.single()
        if not parent_rec:
            raise HTTPException(status_code=404, detail="Parent node not found")

    props = [
        "name: $name",
        "parent_id: $parent_id",
        "atomic: $atomic",
        "reusable: $reusable",
        "connection_type: $connection_type",
        "level: $level",
    ]
    if node.atomic:
        props.append("weight: $weight")
    props.append("recyclable: $recyclable")
    query = (
        "MATCH (p:Project) WHERE id(p)=$pid "
        "MATCH (m:Material) WHERE id(m)=$mid "
        f"CREATE (n:Node {{{', '.join(props)}}})-[:USES]->(m), "
        "(n)-[:PART_OF]->(p) RETURN id(n) AS id"
    )
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

    try:
        result = await session.run(
            query,
            pid=node.project_id,
            mid=node.material_id,
            name=node.name,
            parent_id=node.parent_id,
            atomic=node.atomic,
            reusable=node.reusable,
            connection_type=ctype_db_val,
            level=node.level,
            **({"weight": node.weight} if node.atomic else {}),
            recyclable=node.recyclable,
        )
    except exceptions.ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Neo4j unavailable")

    record = await result.single()
    if not record:
        raise HTTPException(status_code=404, detail="Resource not found")

    node_data = {
        "id":          record["id"],
        "project_id":  node.project_id,
        "material_id": node.material_id,
        "name":        node.name,
        "parent_id":   node.parent_id,
        "atomic":      node.atomic,
        "reusable":    node.reusable,
        "connection_type": ctype_resp,
        "level":       node.level,
        "weight":      node.weight if node.atomic else None,
        "recyclable":  node.recyclable,
    }

    await broadcast(node.project_id, {"op": "create_node", "node": node_data})
    return Node(**node_data)


@router.get("/{node_id}", response_model=Node)
async def get_node(
    node_id: int,
    session: AsyncSession = Depends(get_session),
):
    query = (
        "MATCH (n:Node)-[:USES]->(m:Material) WHERE id(n)=$id "
        "MATCH (n)-[:PART_OF]->(p:Project) "
        "RETURN id(n) AS id, id(p) AS project_id, id(m) AS material_id, "
        "n.name AS name, n.parent_id AS parent_id, n.atomic AS atomic, "
        "n.reusable AS reusable, n.connection_type AS connection_type, "
        "n.level AS level, n.weight AS weight, n.recyclable AS recyclable"
    )
    try:
        result = await session.run(query, id=node_id)
    except exceptions.ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Neo4j unavailable")
    record = await result.single()
    if not record:
        raise HTTPException(status_code=404, detail="Node not found")
    data = record.data()
    ctype_val = data.get("connection_type")
    if isinstance(ctype_val, int):
        try:
            data["connection_type"] = ConnectionType(ctype_val).name
        except ValueError:
            data["connection_type"] = str(ctype_val)
    return Node(**data)


@router.delete("/{node_id}")
async def delete_node(
    node_id: int,
    session: AsyncSession = Depends(get_write_session),
):
    try:
        result = await session.run(
            "MATCH (n:Node)-[:PART_OF]->(p) WHERE id(n)=$id "
            "RETURN id(p) AS pid",
            id=node_id,
        )
    except exceptions.ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Neo4j unavailable")
    rec = await result.single()
    pid = rec["pid"] if rec else 0
    try:
        await session.run(
            "MATCH (n:Node) WHERE id(n)=$id DETACH DELETE n",
            id=node_id,
        )
    except exceptions.ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Neo4j unavailable")
    await broadcast(pid, {"op": "delete_node", "id": node_id})
    return {"ok": True}
