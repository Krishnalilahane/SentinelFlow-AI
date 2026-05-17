from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import (
    AgentRun,
    Case,
    CaseEventType,
    CaseState,
    Decision,
    HumanReview,
    RiskScore,
)
from app.db.session import get_db
from app.schemas.workflow_schema import (
    HumanReviewRequest,
    HumanReviewResponse,
    WorkflowRunResponse,
    WorkflowStatusResponse,
)
from app.services.event_service import create_case_event
from app.services.workflow_service import run_case_workflow


router = APIRouter(prefix="/workflows", tags=["Workflows"])


def _agent_run_to_dict(agent_run: AgentRun) -> dict:
    return {
        "agent_name": agent_run.agent_name,
        "status": agent_run.status,
        "output_payload": agent_run.output_payload,
        "created_at": agent_run.created_at.isoformat() if agent_run.created_at else None,
    }


def _risk_score_to_dict(risk_score: RiskScore | None) -> dict | None:
    if not risk_score:
        return None

    return {
        "fraud_risk_score": risk_score.fraud_risk_score,
        "compliance_risk_score": risk_score.compliance_risk_score,
        "customer_harm_score": risk_score.customer_harm_score,
        "overall_risk_level": risk_score.overall_risk_level,
        "confidence_score": risk_score.confidence_score,
        "reasoning": risk_score.reasoning,
        "created_at": risk_score.created_at.isoformat() if risk_score.created_at else None,
    }


def _decision_to_dict(decision: Decision | None) -> dict | None:
    if not decision:
        return None

    return {
        "decision_type": decision.decision_type,
        "recommendation": decision.recommendation,
        "explanation": decision.explanation,
        "requires_human_review": decision.requires_human_review,
        "created_at": decision.created_at.isoformat() if decision.created_at else None,
    }


@router.post("/cases/{case_id}/run", response_model=WorkflowRunResponse)
def run_workflow_for_case(case_id: str, db: Session = Depends(get_db)):
    try:
        return run_case_workflow(db=db, case_id=case_id)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow execution failed: {str(error)}",
        )


@router.get("/cases/{case_id}/status", response_model=WorkflowStatusResponse)
def get_workflow_status(case_id: str, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found.",
        )

    latest_agent_runs = (
        db.query(AgentRun)
        .filter(AgentRun.case_id == case_id)
        .order_by(AgentRun.created_at.desc())
        .limit(5)
        .all()
    )

    latest_risk_score = (
        db.query(RiskScore)
        .filter(RiskScore.case_id == case_id)
        .order_by(RiskScore.created_at.desc())
        .first()
    )

    latest_decision = (
        db.query(Decision)
        .filter(Decision.case_id == case_id)
        .order_by(Decision.created_at.desc())
        .first()
    )

    latest_human_review = (
        db.query(HumanReview)
        .filter(HumanReview.case_id == case_id)
        .order_by(HumanReview.created_at.desc())
        .first()
    )

    return {
        "case_id": case.id,
        "current_state": case.state,
        "latest_agent_runs": [_agent_run_to_dict(run) for run in latest_agent_runs],
        "latest_risk_score": _risk_score_to_dict(latest_risk_score),
        "latest_decision": _decision_to_dict(latest_decision),
        "human_review_status": latest_human_review.review_status if latest_human_review else None,
    }


@router.post("/cases/{case_id}/human-review", response_model=HumanReviewResponse)
def submit_human_review(
    case_id: str,
    request: HumanReviewRequest,
    db: Session = Depends(get_db),
):
    case = db.query(Case).filter(Case.id == case_id).first()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found.",
        )

    human_review = (
        db.query(HumanReview)
        .filter(HumanReview.case_id == case_id)
        .order_by(HumanReview.created_at.desc())
        .first()
    )

    if not human_review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No human review record found for this case.",
        )

    human_review.review_status = request.review_status
    human_review.reviewer_notes = request.reviewer_notes
    human_review.final_decision = request.final_decision
    human_review.updated_at = datetime.utcnow()

    case.state = CaseState.CLOSED.value
    case.updated_at = datetime.utcnow()

    create_case_event(
        db=db,
        case_id=case.id,
        event_type=CaseEventType.HUMAN_REVIEW_COMPLETED,
        message=f"Human review completed with final decision: {request.final_decision}.",
    )

    db.commit()
    db.refresh(case)
    db.refresh(human_review)

    return {
        "case_id": case.id,
        "review_status": human_review.review_status,
        "final_decision": human_review.final_decision,
        "current_state": case.state,
    }