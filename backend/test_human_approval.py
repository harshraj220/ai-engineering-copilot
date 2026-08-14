import asyncio

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.types import Command

from app.agents.graph import build_agent_graph
from app.core.config import settings


async def main():
    async with AsyncPostgresSaver.from_conn_string(
        settings.CHECKPOINT_DATABASE_URL
    ) as checkpointer:

        await checkpointer.setup()

        graph = build_agent_graph(checkpointer)

        config = {
            "configurable": {
                "thread_id": "demo-human-approval-001"
            }
        }

        result = await graph.ainvoke(
            {
                "task": (
                    "Create a secure FastAPI endpoint that deletes "
                    "a user's account."
                )
            },
            config=config,
        )

        print("\n=== GRAPH PAUSED ===")
        print(result.get("__interrupt__"))

        print("\n=== RESUMING WITH APPROVAL ===")

        final_result = await graph.ainvoke(
            Command(
                resume={
                    "approved": True
                }
            ),
            config=config,
        )

        print("\n=== FINAL RESULT ===")
        print(final_result.get("final_result"))


if __name__ == "__main__":
    asyncio.run(main())