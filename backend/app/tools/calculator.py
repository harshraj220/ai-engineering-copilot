def calculate(expression: str) -> str:
    """
    Calculate a basic arithmetic expression.
    """

    allowed = set("0123456789+-*/(). ")

    if not expression or any(char not in allowed for char in expression):
        raise ValueError("Invalid arithmetic expression")

    try:
        result = eval(expression, {"__builtins__": {}}, {})
    except Exception as exc:
        raise ValueError("Could not evaluate expression") from exc

    return str(result)