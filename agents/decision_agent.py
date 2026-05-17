from agents.state import WorkflowState


def run_decision_agent(state: WorkflowState) -> WorkflowState:
    case_data = state.get("case_data") or {}
    intake_output = state.get("intake_output") or {}
    risk_output = state.get("risk_output") or {}

    case_type = str(intake_output.get("case_type") or case_data.get("case_type") or "").upper()
    detected_patterns = intake_output.get("detected_patterns") or []

    overall_risk_level = str(risk_output.get("overall_risk_level") or "LOW").upper()
    confidence_score = float(risk_output.get("confidence_score") or 0.0)

    requires_human_review = False
    decision_type = "CLOSE_CASE"
    recommendation = "Close the case with no further action."
    explanation = "Risk level is low and confidence is sufficient."

    if overall_risk_level in ["HIGH", "CRITICAL"]:
        requires_human_review = True

    if confidence_score < 0.65:
        requires_human_review = True

    if case_type == "AML_ESCALATION":
        decision_type = "ESCALATE_TO_AML_TEAM"
        recommendation = "Escalate the case to the AML operations team for compliance review."
        explanation = "AML-related cases require specialist compliance handling."
        requires_human_review = True

    elif "ACCOUNT_TAKEOVER_PATTERN" in detected_patterns:
        decision_type = "FREEZE_ACCOUNT_RECOMMENDED"
        recommendation = "Recommend fraud-team escalation and temporary account freeze pending review."
        explanation = "Account takeover indicators were detected, including login or device-based risk signals."
        requires_human_review = True

    elif overall_risk_level in ["HIGH", "CRITICAL"]:
        decision_type = "ESCALATE_TO_FRAUD_TEAM"
        recommendation = "Escalate the case to the fraud operations team for investigation."
        explanation = "Risk analysis produced a high or critical risk rating."

    elif confidence_score < 0.65:
        decision_type = "REQUEST_MORE_INFORMATION"
        recommendation = "Request more information before making a final decision."
        explanation = "Confidence score is below the required threshold for automatic decisioning."

    elif overall_risk_level == "MEDIUM":
        decision_type = "REQUEST_MORE_INFORMATION"
        recommendation = "Request supporting evidence or additional customer verification."
        explanation = "Medium risk requires more evidence before closure."

    decision_output = {
        "decision_type": decision_type,
        "recommendation": recommendation,
        "explanation": explanation,
        "requires_human_review": requires_human_review,
    }

    state["decision_output"] = decision_output
    state["requires_human_review"] = requires_human_review

    return state