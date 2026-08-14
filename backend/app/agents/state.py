from typing import TypedDict


class AgentState(TypedDict, total=False):
    task: str
    plan: list[str]
    research: str
    code: str
    review: str
    tool_results: list[str]
    approval_status: str
    final_result: str