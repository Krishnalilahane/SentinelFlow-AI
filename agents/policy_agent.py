from agents.state import WorkflowState
from app.services.policy_service import PolicyService


policy_service = PolicyService()


def run_policy_agent(state: WorkflowState) -> WorkflowState:
    case_data = state.get("case_data") or {}
    intake_output = state.get("intake_output") or {}

    case_type = intake_output.get("case_type") or case_data.get("case_type") or ""
    description = case_data.get("description") or ""
    priority = intake_output.get("priority") or case_data.get("priority") or ""

    query = f"{case_type} {description} {priority}".strip()

    policy_results = policy_service.search_policies(query=query, top_k=3)

    state["policy_results"] = policy_results

    return state