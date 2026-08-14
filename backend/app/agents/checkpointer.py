from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.core.config import settings


async def create_checkpointer():
    return AsyncPostgresSaver.from_conn_string(
        settings.DATABASE_URL
    )