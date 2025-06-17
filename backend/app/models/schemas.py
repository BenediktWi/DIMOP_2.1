from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class MaterialBase(BaseModel):
    name: str = Field(..., example="Aluminum")
    weight: float = Field(..., gt=0)


class MaterialCreate(MaterialBase):
    pass


class Material(MaterialBase):
    id: int

    class Config:
        from_attributes = True


class NodeBase(BaseModel):
    project_id: int
    material_id: int
    name: str
    parent_id: int | None = None
    atomic: bool
    reusable: bool
    connection_type: str | None = None
    level: int
    weight: float | None = None
    recyclable: bool

    @model_validator(mode="after")
    def _check_weight_atomic(self) -> "NodeBase":
        if self.atomic and self.weight is None:
            raise ValueError("weight must be provided when node is atomic")
        return self


class NodeCreate(NodeBase):
    pass


class Node(NodeBase):
    id: int

    class Config:
        from_attributes = True


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


class ProjectBase(BaseModel):
    name: str


class ProjectCreate(ProjectBase):
    pass


class Project(ProjectBase):
    id: int

    class Config:
        from_attributes = True
