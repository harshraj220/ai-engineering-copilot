from openai import AsyncOpenAI

from app.core.config import settings


class LLMService:
    def __init__(self) -> None:
        self.client = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
        )
        self.model = settings.DEEPSEEK_MODEL

    async def chat(
        self,
        messages: list[dict],
        *,
        tools: list[dict] | None = None,
    ):
        return await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
        )


llm_service = LLMService()