import json

from app.agents.state import AgentState
from app.services.llm import llm_service
from langgraph.types import interrupt

async def human_approval_node(state: AgentState) -> AgentState:
    decision = interrupt(
        {
            "type": "human_approval",
            "message": "Approve this implementation for execution?",
            "task": state["task"],
            "plan": state.get("plan", []),
            "code": state.get("code", ""),
            "review": state.get("review", ""),
        }
    )

    approved = bool(decision.get("approved", False))

    return {
        **state,
        "approval_status": "approved" if approved else "rejected",
    }

async def planner_node(state: AgentState) -> AgentState:
    response = await llm_service.chat(
        [
            {
                "role": "system",
                "content": (
                    "You are the planning agent in an AI Engineering Copilot. "
                    "Break the user's task into 3-5 concrete steps. "
                    "Return ONLY a JSON array of strings."
                ),
            },
            {
                "role": "user",
                "content": state["task"],
            },
        ]
    )

    content = response.choices[0].message.content or "[]"

    try:
        plan = json.loads(content)
    except json.JSONDecodeError:
        plan = [content]

    return {
        **state,
        "plan": plan,
    }


async def researcher_node(state: AgentState) -> AgentState:
    plan = "\n".join(
        f"{index + 1}. {step}"
        for index, step in enumerate(state.get("plan", []))
    )

    response = await llm_service.chat(
        [
            {
                "role": "system",
                "content": (
                    "You are the research agent. "
                    "Analyze the task and planning steps. "
                    "Identify important technical considerations, "
                    "risks, assumptions, and information needed."
                ),
            },
            {
                "role": "user",
                "content": f"""
Task:
{state["task"]}

Plan:
{plan}
""",
            },
        ]
    )

    return {
        **state,
        "research": response.choices[0].message.content or "",
    }


async def coder_node(state: AgentState) -> AgentState:
    response = await llm_service.chat(
        [
            {
                "role": "system",
                "content": (
                    "You are the coding agent. "
                    "Based on the task, plan, and research, "
                    "propose an implementation. "
                    "Return clear code or implementation steps."
                ),
            },
            {
                "role": "user",
                "content": f"""
Task:
{state["task"]}

Plan:
{state.get("plan", [])}

Research:
{state.get("research", "")}
""",
            },
        ]
    )

    return {
        **state,
        "code": response.choices[0].message.content or "",
    }


async def reviewer_node(state: AgentState) -> AgentState:
    response = await llm_service.chat(
        [
            {
                "role": "system",
                "content": (
                    "You are the review agent. "
                    "Review the proposed implementation for correctness, "
                    "security, maintainability, and missing requirements. "
                    "End with exactly one of: APPROVED or REJECTED."
                ),
            },
            {
                "role": "user",
                "content": f"""
Task:
{state["task"]}

Research:
{state.get("research", "")}

Implementation:
{state.get("code", "")}
""",
            },
        ]
    )

    review = response.choices[0].message.content or ""

    approval_status = (
        "approved"
        if "APPROVED" in review.upper()
        else "rejected"
    )

    return {
        **state,
        "review": review,
        "approval_status": approval_status,
    }


async def executor_node(state: AgentState) -> AgentState:
    return {
        **state,
        "final_result": (
            "Implementation approved and ready for execution.\n\n"
            f"Review:\n{state.get('review', '')}"
        ),
    }