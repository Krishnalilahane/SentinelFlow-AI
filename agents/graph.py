from langgraph.graph import END, StateGraph

from agents.decision_agent import run_decision_agent
from agents.human_review_agent import run_human_review_agent
from agents.intake_agent import run_intake_agent
from agents.policy_agent import run_policy_agent
from agents.risk_agent import run_risk_agent
from agents.state import WorkflowState


def close_case_node(state: WorkflowState) -> WorkflowState:
    state["final_status"] = "CLOSED"
    return state


def route_after_decision(state: WorkflowState) -> str:
    if state.get("requires_human_review"):
        return "human_review"

    return "close_case"


def build_workflow_graph():
    graph = StateGraph(WorkflowState)

    graph.add_node("intake", run_intake_agent)
    graph.add_node("retrieve_policy", run_policy_agent)
    graph.add_node("analyse_risk", run_risk_agent)
    graph.add_node("make_decision", run_decision_agent)
    graph.add_node("human_review", run_human_review_agent)
    graph.add_node("close_case", close_case_node)

    graph.set_entry_point("intake")

    graph.add_edge("intake", "retrieve_policy")
    graph.add_edge("retrieve_policy", "analyse_risk")
    graph.add_edge("analyse_risk", "make_decision")

    graph.add_conditional_edges(
        "make_decision",
        route_after_decision,
        {
            "human_review": "human_review",
            "close_case": "close_case",
        },
    )

    graph.add_edge("human_review", END)
    graph.add_edge("close_case", END)

    return graph.compile()


workflow_graph = build_workflow_graph()