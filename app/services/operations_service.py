from datetime import datetime
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models import (
    AgentRun,
    Case,
    CaseEvent,
    CaseEventType,
    CaseState,
    HumanReview,
    HumanReviewStatus,
    RiskScore,
)
from app.services.event_service import create_case_event
from app.services.workflow_service import run_case_workflow


def simulate_workflow_failure(
    db: Session,
    case_id: str,
    failure_reason: str,
) -> dict[str, Any]:
    case = db.query(Case).filter(Case.id == case_id).first()

    if not case:
        raise ValueError("Case not found.")

    previous_state = case.state

    if case.state == CaseState.CLOSED.value:
        raise ValueError("Closed cases cannot be marked as failed.")

    case.state = CaseState.FAILED.value
    case.updated_at = datetime.utcnow()

    create_case_event(
        db=db,
        case_id=case.id,
        event_type=CaseEventType.WORKFLOW_FAILED,
        message=f"Simulated workflow failure: {failure_reason}",
    )

    db.commit()
    db.refresh(case)

    return {
        "case_id": case.id,
        "previous_state": previous_state,
        "current_state": case.state,
        "failure_reason": failure_reason,
        "event_logged": CaseEventType.WORKFLOW_FAILED.value,
    }


def retry_failed_workflow(db: Session, case_id: str) -> dict[str, Any]:
    case = db.query(Case).filter(Case.id == case_id).first()

    if not case:
        raise ValueError("Case not found.")

    previous_state = case.state

    if case.state == CaseState.CLOSED.value:
        return {
            "case_id": case.id,
            "retry_allowed": False,
            "previous_state": previous_state,
            "current_state": case.state,
            "message": "Retry blocked because the case is already closed.",
            "workflow_result": None,
        }

    if case.state == CaseState.WAITING_FOR_HUMAN.value:
        return {
            "case_id": case.id,
            "retry_allowed": False,
            "previous_state": previous_state,
            "current_state": case.state,
            "message": "Retry blocked because the workflow is waiting for human review.",
            "workflow_result": None,
        }

    if case.state != CaseState.FAILED.value:
        return {
            "case_id": case.id,
            "retry_allowed": False,
            "previous_state": previous_state,
            "current_state": case.state,
            "message": "Retry is only allowed for FAILED cases.",
            "workflow_result": None,
        }

    create_case_event(
        db=db,
        case_id=case.id,
        event_type=CaseEventType.WORKFLOW_STARTED,
        message="Workflow retry requested after failure.",
    )
    db.commit()

    workflow_result = run_case_workflow(db=db, case_id=case.id)

    refreshed_case = db.query(Case).filter(Case.id == case_id).first()

    return {
        "case_id": case.id,
        "retry_allowed": True,
        "previous_state": previous_state,
        "current_state": refreshed_case.state if refreshed_case else workflow_result.get("current_state"),
        "message": "Retry executed successfully.",
        "workflow_result": workflow_result,
    }


def compensate_case_workflow(
    db: Session,
    case_id: str,
    compensation_action: str,
    reason: str,
) -> dict[str, Any]:
    case = db.query(Case).filter(Case.id == case_id).first()

    if not case:
        raise ValueError("Case not found.")

    allowed_actions = {
        "UNFREEZE_ACCOUNT_RECOMMENDED",
        "CANCEL_FRAUD_ESCALATION",
        "REQUEST_MANUAL_REVIEW",
        "REOPEN_CASE",
        "NOTIFY_OPERATIONS_TEAM",
    }

    if compensation_action not in allowed_actions:
        raise ValueError(
            "Invalid compensation action. Use one of: "
            + ", ".join(sorted(allowed_actions))
        )

    clean_reason = reason.rstrip(".")

    message = (
        f"Simulated compensation action recorded: {compensation_action}. "
        f"Reason: {clean_reason}. No real banking action was executed."
    )

    create_case_event(
        db=db,
        case_id=case.id,
        event_type=CaseEventType.WORKFLOW_FAILED,
        message=message,
    )

    if compensation_action == "REOPEN_CASE" and case.state == CaseState.CLOSED.value:
        case.state = CaseState.FAILED.value
        case.updated_at = datetime.utcnow()

    db.commit()

    return {
        "case_id": case.id,
        "compensation_action": compensation_action,
        "reason": reason,
        "event_logged": CaseEventType.WORKFLOW_FAILED.value,
        "message": message,
    }


def get_operations_metrics(db: Session) -> dict[str, Any]:
    total_cases = db.query(Case).count()

    state_rows = (
        db.query(Case.state, func.count(Case.id))
        .group_by(Case.state)
        .all()
    )

    cases_by_state = {state: count for state, count in state_rows}

    human_review_pending_count = (
        db.query(HumanReview)
        .filter(HumanReview.review_status == HumanReviewStatus.PENDING.value)
        .count()
    )

    closed_cases_count = (
        db.query(Case)
        .filter(Case.state == CaseState.CLOSED.value)
        .count()
    )

    high_or_critical_risk_count = (
        db.query(RiskScore)
        .filter(RiskScore.overall_risk_level.in_(["HIGH", "CRITICAL"]))
        .count()
    )

    total_agent_runs = db.query(AgentRun).count()
    total_workflow_events = db.query(CaseEvent).count()

    average_confidence_score = db.query(func.avg(RiskScore.confidence_score)).scalar()

    return {
        "total_cases": total_cases,
        "cases_by_state": cases_by_state,
        "human_review_pending_count": human_review_pending_count,
        "closed_cases_count": closed_cases_count,
        "high_or_critical_risk_count": high_or_critical_risk_count,
        "total_agent_runs": total_agent_runs,
        "total_workflow_events": total_workflow_events,
        "average_confidence_score": round(float(average_confidence_score), 4)
        if average_confidence_score is not None
        else None,
    }