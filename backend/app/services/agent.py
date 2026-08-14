import json

from app.services.llm import llm_service
from app.tools.registry import TOOL_FUNCTIONS, TOOLS


class AgentService:

    async def run(self, user_message: str) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an AI Engineering Copilot. "
                    "Use tools when they are useful."
                ),
            },
            {
                "role": "user",
                "content": user_message,
            },
        ]

        response = await llm_service.chat(
            messages,
            tools=TOOLS,
        )

        message = response.choices[0].message

        if not message.tool_calls:
            return message.content or ""

        messages.append(message)

        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            tool_function = TOOL_FUNCTIONS.get(function_name)

            if tool_function is None:
                raise ValueError(f"Unknown tool: {function_name}")

            result = tool_function(**arguments)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                }
            )

        final_response = await llm_service.chat(messages)

        return final_response.choices[0].message.content or ""


agent_service = AgentService()