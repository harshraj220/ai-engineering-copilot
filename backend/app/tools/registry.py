from app.tools.calculator import calculate


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Calculate a basic arithmetic expression.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Arithmetic expression such as 25 * 4",
                    }
                },
                "required": ["expression"],
                "additionalProperties": False,
            },
        },
    }
]


TOOL_FUNCTIONS = {
    "calculate": calculate,
}