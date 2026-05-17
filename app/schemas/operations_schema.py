from pydantic import BaseModel, Field


class SimulateFailureRequest(BaseModel):
    failure_reason: str = Field(
        default="Simulated downstream workflow failure",
        min_length=3,
        max_length=500,
    )


class SimulateFailureResponse(BaseModel):
    case_id: str
    previous_state: str
    current_state: str
    failure_reason: str
    event_logged: str


class RetryWorkflowResponse(BaseModel):
    case_id: str
    retry_allowed: bool
    previous_state: str
    current_state: str
    message: str
    workflow_result: dict | None = None


class CompensationRequest(BaseModel):
    compensation_action: str = Field(
        default="REQUEST_MANUAL_REVIEW",
        min_length=3,
        max_length=100,
    )
    reason: str = Field(
        default="Simulated compensation for workflow recovery demonstration",
        min_length=3,
        max_length=500,
    )


class CompensationResponse(BaseModel):
    case_id: str
    compensation_action: str
    reason: str
    event_logged: str
    message: str


class OperationsMetricsResponse(BaseModel):
    total_cases: int
    cases_by_state: dict[str, int]
    human_review_pending_count: int
    closed_cases_count: int
    high_or_critical_risk_count: int
    total_agent_runs: int
    total_workflow_events: int
    average_confidence_score: float | None
