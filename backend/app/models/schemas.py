from __future__ import annotations

from pydantic import BaseModel, Field


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
    weight: float
    recyclable: bool


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
