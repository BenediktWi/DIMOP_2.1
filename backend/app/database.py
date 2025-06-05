from typing import AsyncGenerator
import os

from neo4j import AsyncGraphDatabase, AsyncSession, exceptions


def get_driver(uri: str, user: str | None = None, password: str | None = None):
    return AsyncGraphDatabase.driver(uri, auth=(user or None, password or None))


driver = get_driver(
    uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    user=os.getenv("NEO4J_USER", "neo4j"),
    password=os.getenv("NEO4J_PASSWORD", "your_password"),
)

async def verify_connectivity() -> None:
    """Ensure the Neo4j database is reachable."""
    try:
        await driver.verify_connectivity()
    except exceptions.ServiceUnavailable as exc:
        raise RuntimeError("Unable to connect to Neo4j") from exc


async def get_session(*, write: bool = False) -> AsyncGenerator[AsyncSession, None]:
    async with driver.session(
        default_access_mode="WRITE" if write else "READ"
    ) as session:
        yield session
