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
    level: int
    parent_id: int | None = None


class NodeCreate(NodeBase):
    @model_validator(mode="after")
    def check_parent_id(cls, values: "NodeCreate") -> "NodeCreate":
        if values.level == 0 and values.parent_id is not None:
            raise ValueError("level 0 nodes cannot have a parent")
        if values.level > 0 and values.parent_id is None:
            raise ValueError("non-root nodes must define parent_id")
        return values


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
