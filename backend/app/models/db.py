from __future__ import annotations

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Material(Base):
    __tablename__ = "materials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    co2_value: Mapped[float] = mapped_column(Float, nullable=False)
    hardness: Mapped[float] = mapped_column(Float, nullable=False)


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)


class Node(Base):
    __tablename__ = "nodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    material_id: Mapped[int] = mapped_column(ForeignKey("materials.id"))
    name: Mapped[str] = mapped_column(String, nullable=False)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("nodes.id"), nullable=True)
    atomic: Mapped[bool] = mapped_column(Boolean, nullable=False)
    reusable: Mapped[bool] = mapped_column(Boolean, nullable=False)
    connection_type: Mapped[int | None] = mapped_column(Integer, nullable=True)
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    weight: Mapped[float | None] = mapped_column(Float, nullable=True)
    recyclable: Mapped[bool] = mapped_column(Boolean, nullable=False)
    sustainability_score: Mapped[float | None] = mapped_column(Float, nullable=True)


class Relation(Base):
    __tablename__ = "relations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    source_id: Mapped[int] = mapped_column(ForeignKey("nodes.id"))
    target_id: Mapped[int] = mapped_column(ForeignKey("nodes.id"))


