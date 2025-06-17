from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# Materials
# ---------------------------------------------------------------------------


class MaterialBase(BaseModel):
    name: str = Field(..., example="Aluminum")
    weight: float = Field(..., gt=0)
    co2_value: float = Field(..., gt=0)
    hardness: float = Field(..., gt=0)  # kept from Development_Nachhaltigkeit


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
    connection_type: str | int | None = None
    level: int
    weight: float | None = Field(None, gt=0)
    recyclable: bool

    @model_validator(mode="after")
    def _check_weight_atomic(self) -> "NodeBase":
        """If a node is atomic it must carry its own weight."""
        if self.atomic and self.weight is None:
            raise ValueError("weight must be provided when node is atomic")
        return self

    @model_validator(mode="after")
    def _validate_connection_type(self) -> "NodeBase":
        """Ensure connection_type is either within range when numeric or any string."""
        if isinstance(self.connection_type, int):
            if not 0 <= self.connection_type <= 5:
                raise ValueError("connection_type numeric must be between 0 and 5")
        elif self.connection_type is not None and not isinstance(
            self.connection_type, str
        ):
            raise ValueError("connection_type must be int, str, or None")
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
# Sustainability score tracking (from implement-sustainability-score-tracking)
# ---------------------------------------------------------------------------


class NodeScore(BaseModel):
    id: int
    sustainability_score: float
