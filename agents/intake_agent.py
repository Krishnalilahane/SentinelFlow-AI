from agents.state import WorkflowState


ACCOUNT_TAKEOVER_KEYWORDS = [
    "new device",
    "failed login",
    "failed logins",
    "unknown transaction",
    "unknown card transaction",
    "account access",
    "password reset",
    "contact detail change",
]

FRAUD_KEYWORDS = [
    "fraud",
    "suspicious",
    "unauthorised",
    "unauthorized",
    "unknown",
    "card transaction",
]

AML_KEYWORDS = [
    "aml",
    "money laundering",
    "sanctions",
    "suspicious activity",
    "source of funds",
]


def run_intake_agent(state: WorkflowState) -> WorkflowState:
    case_data = state.get("case_data") or {}

    description = str(case_data.get("description") or "").lower()
    case_type = str(case_data.get("case_type") or "").upper()
    priority = str(case_data.get("priority") or "LOW").upper()

    missing_fields: list[str] = []

    if not case_data.get("customer_id"):
        missing_fields.append("customer_id")

    if not case_data.get("transaction_id"):
        missing_fields.append("transaction_id")

    if not case_data.get("description"):
        missing_fields.append("description")

    detected_patterns: list[str] = []

    if any(keyword in description for keyword in ACCOUNT_TAKEOVER_KEYWORDS):
        detected_patterns.append("ACCOUNT_TAKEOVER_PATTERN")

    if any(keyword in description for keyword in FRAUD_KEYWORDS):
        detected_patterns.append("FRAUD_PATTERN")

    if case_type == "AML_ESCALATION" or any(keyword in description for keyword in AML_KEYWORDS):
        detected_patterns.append("AML_PATTERN")

    inferred_case_type = case_type

    if "AML_PATTERN" in detected_patterns:
        inferred_case_type = "AML_ESCALATION"
    elif "ACCOUNT_TAKEOVER_PATTERN" in detected_patterns or "FRAUD_PATTERN" in detected_patterns:
        inferred_case_type = case_type or "SUSPICIOUS_TRANSACTION"

    if priority in ["HIGH", "CRITICAL"]:
        urgency_level = "HIGH"
    elif missing_fields:
        urgency_level = "MEDIUM"
    else:
        urgency_level = "LOW"

    extracted_summary = (
        f"Case {case_data.get('id')} for customer {case_data.get('customer_id')} "
        f"relates to {inferred_case_type}. Detected patterns: "
        f"{', '.join(detected_patterns) if detected_patterns else 'NONE'}."
    )

    intake_output = {
        "case_type": inferred_case_type,
        "priority": priority,
        "missing_fields": missing_fields,
        "urgency_level": urgency_level,
        "detected_patterns": detected_patterns,
        "extracted_summary": extracted_summary,
    }

    state["intake_output"] = intake_output
    state["requires_human_review"] = False

    return state