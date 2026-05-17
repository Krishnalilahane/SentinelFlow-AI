from pydantic import BaseModel, Field


class WorkflowRunResponse(BaseModel):
    case_id: str
    final_status: str | None
    current_state: str
    requires_human_review: bool
    risk_summary: dict
    decision_summary: dict
    events_created: list[str]


class WorkflowStatusResponse(BaseModel):
    case_id: str
    current_state: str
    latest_agent_runs: list[dict]
    latest_risk_score: dict | None
    latest_decision: dict | None
    human_review_status: str | None


class HumanReviewRequest(BaseModel):
    review_status: str = Field(..., pattern="^(APPROVED|REJECTED|ESCALATED)$")
    reviewer_notes: str = Field(..., min_length=5, max_length=2000)
    final_decision: str = Field(..., min_length=3, max_length=80)


class HumanReviewResponse(BaseModel):
    case_id: str
    review_status: str
    final_decision: str
    current_state: str