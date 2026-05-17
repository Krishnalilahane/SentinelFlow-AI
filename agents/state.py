from typing import Any, TypedDict


class WorkflowState(TypedDict, total=False):
    case_id: str
    run_id: str

    case_data: dict[str, Any]

    intake_output: dict[str, Any]
    policy_results: list[dict[str, Any]]
    risk_output: dict[str, Any]
    decision_output: dict[str, Any]

    requires_human_review: bool
    human_review_status: str | None

    errors: list[str]
    final_status: str