import sys
from pathlib import Path

import requests
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))

from ui_helpers import (
    case_display_name,
    format_label,
    format_number,
    short_id,
)


API_BASE_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="Human Review | SentinelFlow AI",
    page_icon="👤",
    layout="wide",
)


def get_cases() -> list[dict]:
    response = requests.get(f"{API_BASE_URL}/cases", timeout=15)
    response.raise_for_status()
    return response.json()


def get_workflow_status(case_id: str) -> dict:
    response = requests.get(f"{API_BASE_URL}/workflows/cases/{case_id}/status", timeout=15)
    response.raise_for_status()
    return response.json()


def submit_human_review(
    case_id: str,
    review_status: str,
    reviewer_notes: str,
    final_decision: str,
) -> dict:
    response = requests.post(
        f"{API_BASE_URL}/workflows/cases/{case_id}/human-review",
        json={
            "review_status": review_status,
            "reviewer_notes": reviewer_notes,
            "final_decision": final_decision,
        },
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


st.title("Human Review Queue")
st.caption("Review AI recommendations before a case is closed.")

try:
    cases = get_cases()
    pending_cases = [
        case for case in cases if case["state"] == "WAITING_FOR_HUMAN"
    ]

    if not pending_cases:
        st.success("No cases are currently waiting for human review.")
        st.stop()

    st.info(f"{len(pending_cases)} case(s) need human review.")

    case_options = {
        case_display_name(case): case
        for case in pending_cases
    }

    selected_label = st.selectbox(
        "Choose a case to review",
        options=list(case_options.keys()),
    )

    selected_case = case_options[selected_label]
    case_id = selected_case["id"]

    st.subheader("Case Summary")

    col1, col2, col3, col4 = st.columns(4)

    col1.write("**Priority**")
    col1.warning(format_label(selected_case["priority"]))

    col2.write("**Case Type**")
    col2.info(format_label(selected_case["case_type"]))

    col3.write("**Status**")
    col3.warning(format_label(selected_case["state"]))

    col4.write("**Case ID**")
    col4.code(short_id(selected_case["id"]))

    st.write("**Description:**")
    st.write(selected_case["description"])

    st.divider()

    status = get_workflow_status(case_id)

    risk_score = status.get("latest_risk_score")
    decision = status.get("latest_decision")

    st.subheader("AI Risk Review")

    if risk_score:
        r1, r2, r3, r4 = st.columns(4)

        r1.metric("Fraud Risk", format_number(risk_score["fraud_risk_score"]))
        r2.metric("Compliance Risk", format_number(risk_score["compliance_risk_score"]))
        r3.write("**Risk Level**")
        r3.error(format_label(risk_score["overall_risk_level"]))
        r4.metric("AI Confidence", format_number(risk_score["confidence_score"]))

        st.write("**Why the AI flagged this case:**")
        st.info(risk_score["reasoning"])

    if decision:
        st.write("**AI Recommendation:**")
        st.success(decision["recommendation"])

        st.write("**Decision Explanation:**")
        st.write(decision["explanation"])

    st.divider()

    st.subheader("Submit Final Review")

    review_status_display = st.selectbox(
        "Review outcome",
        options=["Approve", "Reject", "Escalate"],
        index=2,
    )

    review_status_map = {
        "Approve": "APPROVED",
        "Reject": "REJECTED",
        "Escalate": "ESCALATED",
    }

    final_decision_display = st.selectbox(
        "Final decision",
        options=[
            "Escalate To Fraud Team",
            "Approve AI Recommendation",
            "Reject AI Recommendation",
            "Request More Information",
            "Close With No Action",
        ],
    )

    final_decision_map = {
        "Escalate To Fraud Team": "ESCALATE_TO_FRAUD_TEAM",
        "Approve AI Recommendation": "APPROVE_AI_RECOMMENDATION",
        "Reject AI Recommendation": "REJECT_AI_RECOMMENDATION",
        "Request More Information": "REQUEST_MORE_INFORMATION",
        "Close With No Action": "CLOSE_NO_ACTION",
    }

    reviewer_notes = st.text_area(
        "Reviewer notes",
        value="Reviewed AI recommendation and risk evidence. Escalation required for manual fraud operations follow-up.",
        height=120,
    )

    if st.button("Submit Review", type="primary"):
        result = submit_human_review(
            case_id=case_id,
            review_status=review_status_map[review_status_display],
            reviewer_notes=reviewer_notes,
            final_decision=final_decision_map[final_decision_display],
        )

        st.success("Human review submitted successfully.")
        st.json(result)
        st.info("Refresh the page to update the review queue.")

except requests.exceptions.ConnectionError:
    st.error(
        "Could not connect to FastAPI backend. Start it with: "
        "uvicorn app.main:app --reload"
    )

except Exception as error:
    st.error(f"Human review error: {error}")