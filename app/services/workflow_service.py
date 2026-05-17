import uuid
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from agents.graph import workflow_graph
from app.db.models import (
    AgentRun,
    Case,
    CaseEventType,
    CaseState,
    Decision,
    HumanReview,
    HumanReviewStatus,
    RiskScore,
)
from app.services.event_service import create_case_event


def _case_to_dict(case: Case) -> dict[str, Any]:
    return {
        "id": case.id,
        "customer_id": case.customer_id,
        "transaction_id": case.transaction_id,
        "case_type": case.case_type,
        "description": case.description,
        "priority": case.priority,
        "state": case.state,
        "created_at": case.created_at.isoformat() if case.created_at else None,
        "updated_at": case.updated_at.isoformat() if case.updated_at else None,
    }


def _save_agent_run(
    db: Session,
    run_id: str,
    case_id: str,
    agent_name: str,
    input_payload: dict | list | None,
    output_payload: dict | list | None,
    status: str = "COMPLETED",
) -> AgentRun:
    agent_run = AgentRun(
        run_id=run_id,
        case_id=case_id,
        agent_name=agent_name,
        input_payload=input_payload,
        output_payload=output_payload,
        status=status,
    )
    db.add(agent_run)
    db.flush()
    return agent_run


def run_case_workflow(db: Session, case_id: str) -> dict[str, Any]:
    case = db.query(Case).filter(Case.id == case_id).first()

    if not case:
        raise ValueError("Case not found.")

    if case.state == CaseState.WAITING_FOR_HUMAN.value:
        raise ValueError("Workflow is already waiting for human review.")

    if case.state == CaseState.CLOSED.value:
        raise ValueError("Workflow cannot be rerun because the case is already closed.")

    run_id = str(uuid.uuid4())
    events_created: list[str] = []

    try:
        case.state = CaseState.CLASSIFYING.value

        create_case_event(
            db=db,
            case_id=case.id,
            event_type=CaseEventType.WORKFLOW_STARTED,
            message=f"Workflow started. Run ID: {run_id}",
        )
        events_created.append(CaseEventType.WORKFLOW_STARTED.value)

        initial_state = {
            "case_id": case.id,
            "run_id": run_id,
            "case_data": _case_to_dict(case),
            "errors": [],
        }

        final_state = workflow_graph.invoke(initial_state)

        intake_output = final_state.get("intake_output") or {}
        policy_results = final_state.get("policy_results") or []
        risk_output = final_state.get("risk_output") or {}
        decision_output = final_state.get("decision_output") or {}

        _save_agent_run(
            db=db,
            run_id=run_id,
            case_id=case.id,
            agent_name="intake_agent",
            input_payload=initial_state["case_data"],
            output_payload=intake_output,
        )
        create_case_event(
            db=db,
            case_id=case.id,
            event_type=CaseEventType.INTAKE_COMPLETED,
            message="Intake agent completed classification and urgency extraction.",
        )
        events_created.append(CaseEventType.INTAKE_COMPLETED.value)

        case.state = CaseState.RETRIEVING_POLICY.value
        _save_agent_run(
            db=db,
            run_id=run_id,
            case_id=case.id,
            agent_name="policy_retrieval_agent",
            input_payload={
                "case_type": intake_output.get("case_type"),
                "description": case.description,
                "priority": case.priority,
            },
            output_payload={"policy_results": policy_results},
        )
        create_case_event(
            db=db,
            case_id=case.id,
            event_type=CaseEventType.POLICY_RETRIEVED,
            message=f"Policy retrieval completed with {len(policy_results)} result(s).",
        )
        events_created.append(CaseEventType.POLICY_RETRIEVED.value)

        case.state = CaseState.ANALYSING_RISK.value
        _save_agent_run(
            db=db,
            run_id=run_id,
            case_id=case.id,
            agent_name="risk_analysis_agent",
            input_payload={
                "case_data": initial_state["case_data"],
                "intake_output": intake_output,
                "policy_results": policy_results,
            },
            output_payload=risk_output,
        )

        risk_score = RiskScore(
            case_id=case.id,
            fraud_risk_score=risk_output["fraud_risk_score"],
            compliance_risk_score=risk_output["compliance_risk_score"],
            customer_harm_score=risk_output["customer_harm_score"],
            overall_risk_level=risk_output["overall_risk_level"],
            confidence_score=risk_output["confidence_score"],
            reasoning=risk_output["reasoning"],
        )
        db.add(risk_score)

        create_case_event(
            db=db,
            case_id=case.id,
            event_type=CaseEventType.RISK_ANALYSIS_COMPLETED,
            message=f"Risk analysis completed. Overall risk: {risk_output['overall_risk_level']}.",
        )
        events_created.append(CaseEventType.RISK_ANALYSIS_COMPLETED.value)

        case.state = CaseState.DECISION_READY.value
        _save_agent_run(
            db=db,
            run_id=run_id,
            case_id=case.id,
            agent_name="decision_agent",
            input_payload={
                "intake_output": intake_output,
                "risk_output": risk_output,
            },
            output_payload=decision_output,
        )

        decision = Decision(
            case_id=case.id,
            decision_type=decision_output["decision_type"],
            recommendation=decision_output["recommendation"],
            explanation=decision_output["explanation"],
            requires_human_review=decision_output["requires_human_review"],
        )
        db.add(decision)

        create_case_event(
            db=db,
            case_id=case.id,
            event_type=CaseEventType.DECISION_GENERATED,
            message=f"Decision generated: {decision_output['decision_type']}.",
        )
        events_created.append(CaseEventType.DECISION_GENERATED.value)

        requires_human_review = bool(final_state.get("requires_human_review"))

        if requires_human_review:
            case.state = CaseState.WAITING_FOR_HUMAN.value

            existing_review = (
                db.query(HumanReview)
                .filter(
                    HumanReview.case_id == case.id,
                    HumanReview.review_status == HumanReviewStatus.PENDING.value,
                )
                .first()
            )

            if not existing_review:
                db.add(
                    HumanReview(
                        case_id=case.id,
                        review_status=HumanReviewStatus.PENDING.value,
                    )
                )

            create_case_event(
                db=db,
                case_id=case.id,
                event_type=CaseEventType.HUMAN_REVIEW_REQUIRED,
                message="Workflow paused for human review.",
            )
            events_created.append(CaseEventType.HUMAN_REVIEW_REQUIRED.value)

        else:
            case.state = CaseState.CLOSED.value
            create_case_event(
                db=db,
                case_id=case.id,
                event_type=CaseEventType.WORKFLOW_COMPLETED,
                message="Workflow completed without human review.",
            )
            events_created.append(CaseEventType.WORKFLOW_COMPLETED.value)

        case.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(case)

        return {
            "case_id": case.id,
            "final_status": final_state.get("final_status"),
            "current_state": case.state,
            "requires_human_review": requires_human_review,
            "risk_summary": risk_output,
            "decision_summary": decision_output,
            "events_created": events_created,
        }

    except Exception as error:
        case.state = CaseState.FAILED.value
        case.updated_at = datetime.utcnow()

        create_case_event(
            db=db,
            case_id=case.id,
            event_type=CaseEventType.WORKFLOW_FAILED,
            message=f"Workflow failed: {str(error)}",
        )

        db.commit()
        raise