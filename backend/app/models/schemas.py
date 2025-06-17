from __future__ import annotations

from enum import IntEnum
from pydantic import BaseModel, Field, model_validator


class ConnectionType(IntEnum):
    """Supported connection types between components."""

    SCREW = 0
    BOLT = 1
    GLUE = 2
    WELD = 3
    NAIL = 4
    CLIP = 5


# ---------------------------------------------------------------------------
# Materials
# ---------------------------------------------------------------------------

class MaterialBase(BaseModel):
    name: str = Field(..., example="Aluminum")
    weight: float = Field(..., gt=0)
    co2_value: float = Field(..., gt=0)
    hardness: float = Field(..., gt=0)  # retained from Development_Nachhaltigkeit


class MaterialCreate(MaterialBase):
    pass


class Material(MaterialBase):
    id: int

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------

class NodeBase(BaseModel):
    project_id: int
    material_id: int
    name: str
    parent_id: int | None = None
    atomic: bool
    reusable: bool
    # allow both Enum values and custom string identifiers
    connection_type: ConnectionType | str | None = None
    level: int
    weight: float | None = Field(None, gt=0)
    recyclable: bool

    # ---- Validators -------------------------------------------------------

    @model_validator(mode="after")
    def _check_weight_atomic(self) -> "NodeBase":
        """
        Atomic nodes must have an explicit weight;
        group nodes get their weight calculated later.
        """
        if self.atomic and self.weight is None:
            raise ValueError("weight must be provided when node is atomic")
        return self

    @model_validator(mode="after")
    def _validate_connection_type(self) -> "NodeBase":
        """Validate type of ``connection_type``."""
        if isinstance(self.connection_type, ConnectionType) or self.connection_type is None:
            return self
        if not isinstance(self.connection_type, str):
            raise ValueError("connection_type must be ConnectionType, str, or None")
        return self


class NodeCreate(NodeBase):
    pass


class Node(NodeBase):
    id: int

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Relations
# ---------------------------------------------------------------------------

class RelationBase(BaseModel):
    project_id: int
    source_id: int
    target_id: int


class RelationCreate(RelationBase):
    pass


class Relation(RelationBase):
    id: int

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

class ProjectBase(BaseModel):
    name: str


class ProjectCreate(ProjectBase):
    pass


class Project(ProjectBase):
    id: int

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Sustainability score tracking
# ---------------------------------------------------------------------------

class NodeScore(BaseModel):
    id: int
    sustainability_score: float
