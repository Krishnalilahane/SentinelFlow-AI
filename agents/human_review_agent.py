from agents.state import WorkflowState


def run_human_review_agent(state: WorkflowState) -> WorkflowState:
    state["human_review_status"] = "PENDING"
    state["final_status"] = "WAITING_FOR_HUMAN"
    state["requires_human_review"] = True

    return state