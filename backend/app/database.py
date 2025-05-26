from typing import AsyncGenerator
from contextlib import asynccontextmanager
import os

from neo4j import AsyncGraphDatabase


def get_driver(uri: str, user: str | None = None, password: str | None = None):
    return AsyncGraphDatabase.driver(uri, auth=(user or None, password or None))


driver = get_driver(
    uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    user=os.getenv("NEO4J_USER", "neo4j"),
    password=os.getenv("NEO4J_PASSWORD", "neo4j"),
)


@asynccontextmanager
async def get_session(*, write: bool = False) -> AsyncGenerator:
    async with driver.session(default_access_mode="WRITE" if write else "READ") as session:
        yield session
