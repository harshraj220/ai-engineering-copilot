from langgraph.graph import END, START, StateGraph

from app.agents.nodes import (
    coder_node,
    executor_node,
    human_approval_node,
    planner_node,
    researcher_node,
    reviewer_node,
)
from app.agents.state import AgentState


def build_agent_graph(checkpointer):
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("coder", coder_node)
    graph.add_node("reviewer", reviewer_node)
    graph.add_node("human_approval", human_approval_node)
    graph.add_node("executor", executor_node)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "researcher")
    graph.add_edge("researcher", "coder")
    graph.add_edge("coder", "reviewer")

    graph.add_conditional_edges(
        "reviewer",
        lambda state: (
            "human_approval"
            if state.get("approval_status") == "approved"
            else "coder"
        ),
        {
            "human_approval": "human_approval",
            "coder": "coder",
        },
    )

    graph.add_conditional_edges(
        "human_approval",
        lambda state: state.get("approval_status"),
        {
            "approved": "executor",
            "rejected": "coder",
        },
    )

    graph.add_edge("executor", END)

    return graph.compile(checkpointer=checkpointer)