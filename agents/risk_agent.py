from agents.state import WorkflowState


def _clamp_score(value: float) -> float:
    return max(0.0, min(100.0, value))


def run_risk_agent(state: WorkflowState) -> WorkflowState:
    case_data = state.get("case_data") or {}
    intake_output = state.get("intake_output") or {}
    policy_results = state.get("policy_results") or []

    description = str(case_data.get("description") or "").lower()
    case_type = str(intake_output.get("case_type") or case_data.get("case_type") or "").upper()
    priority = str(intake_output.get("priority") or case_data.get("priority") or "LOW").upper()
    missing_fields = intake_output.get("missing_fields") or []
    detected_patterns = intake_output.get("detected_patterns") or []

    fraud_risk_score = 20.0
    compliance_risk_score = 15.0
    customer_harm_score = 10.0
    confidence_score = 0.85

    reasoning_parts: list[str] = []

    if "new device" in description and ("unknown" in description or "transaction" in description):
        fraud_risk_score += 45
        reasoning_parts.append("New device activity combined with an unknown or suspicious transaction increased fraud risk.")

    if "failed login" in description or "failed logins" in description:
        fraud_risk_score += 25
        reasoning_parts.append("Failed login activity indicates possible account takeover behaviour.")

    if "ACCOUNT_TAKEOVER_PATTERN" in detected_patterns:
        fraud_risk_score += 20
        customer_harm_score += 20
        reasoning_parts.append("Intake detected account takeover indicators.")

    if case_type == "AML_ESCALATION":
        compliance_risk_score += 55
        reasoning_parts.append("AML case type increases compliance risk.")

    policy_text = " ".join(str(result.get("chunk_text", "")).lower() for result in policy_results)

    if "vulnerable customer" in policy_text:
        customer_harm_score += 35
        reasoning_parts.append("Retrieved policy context references vulnerable customer handling.")

    if "fraud" in policy_text or "account takeover" in policy_text:
        fraud_risk_score += 10
        reasoning_parts.append("Retrieved policy context supports fraud or account takeover review.")

    if priority == "CRITICAL":
        fraud_risk_score += 20
        compliance_risk_score += 15
        customer_harm_score += 15
        reasoning_parts.append("Critical priority increases all risk dimensions.")
    elif priority == "HIGH":
        fraud_risk_score += 10
        customer_harm_score += 10
        reasoning_parts.append("High priority increases fraud and customer harm risk.")

    if missing_fields:
        confidence_score -= 0.25
        reasoning_parts.append(f"Missing fields reduce confidence: {', '.join(missing_fields)}.")

    fraud_risk_score = _clamp_score(fraud_risk_score)
    compliance_risk_score = _clamp_score(compliance_risk_score)
    customer_harm_score = _clamp_score(customer_harm_score)
    confidence_score = max(0.0, min(1.0, confidence_score))

    max_score = max(fraud_risk_score, compliance_risk_score, customer_harm_score)

    if max_score >= 85:
        overall_risk_level = "CRITICAL"
    elif max_score >= 65:
        overall_risk_level = "HIGH"
    elif max_score >= 35:
        overall_risk_level = "MEDIUM"
    else:
        overall_risk_level = "LOW"

    risk_output = {
        "fraud_risk_score": fraud_risk_score,
        "compliance_risk_score": compliance_risk_score,
        "customer_harm_score": customer_harm_score,
        "overall_risk_level": overall_risk_level,
        "confidence_score": round(confidence_score, 2),
        "reasoning": " ".join(reasoning_parts) if reasoning_parts else "No major risk indicators detected.",
    }

    state["risk_output"] = risk_output

    return state