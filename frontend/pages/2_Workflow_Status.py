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
    page_title="Workflow Status | SentinelFlow AI",
    page_icon="⚙️",
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


st.title("Workflow Status")
st.caption("See what the AI agents found, scored, and recommended.")

try:
    cases = get_cases()

    if not cases:
        st.warning("No cases found.")
        st.stop()

    case_options = {
        case_display_name(case): case
        for case in cases
    }

    selected_label = st.selectbox(
        "Choose a case",
        options=list(case_options.keys()),
    )

    selected_case = case_options[selected_label]
    case_id = selected_case["id"]

    status = get_workflow_status(case_id)

    st.subheader("Current Status")

    col1, col2, col3 = st.columns(3)

    col1.write("**Case Status**")
    col1.info(format_label(status["current_state"]))

    col2.write("**Human Review**")
    col2.warning(format_label(status["human_review_status"]))

    col3.write("**Case ID**")
    col3.code(short_id(status["case_id"]))

    st.divider()

    st.subheader("Risk Score")

    risk_score = status.get("latest_risk_score")

    if risk_score:
        r1, r2, r3, r4, r5 = st.columns(5)

        r1.metric("Fraud Risk", format_number(risk_score["fraud_risk_score"]))
        r2.metric("Compliance Risk", format_number(risk_score["compliance_risk_score"]))
        r3.metric("Customer Harm", format_number(risk_score["customer_harm_score"]))
        r4.write("**Risk Level**")
        r4.error(format_label(risk_score["overall_risk_level"]))
        r5.metric("AI Confidence", format_number(risk_score["confidence_score"]))

        st.write("**Why this risk score was assigned:**")
        st.info(risk_score["reasoning"])
    else:
        st.info("No risk score found. Run the workflow for this case first.")

    st.divider()

    st.subheader("AI Decision")

    decision = status.get("latest_decision")

    if decision:
        d1, d2 = st.columns(2)

        d1.write("**Decision**")
        d1.success(format_label(decision["decision_type"]))

        d2.write("**Needs Human Review**")
        d2.warning("Yes" if decision["requires_human_review"] else "No")

        st.write("**AI Recommendation:**")
        st.success(decision["recommendation"])

        st.write("**Explanation:**")
        st.write(decision["explanation"])
    else:
        st.info("No decision found. Run the workflow for this case first.")

    st.divider()

    st.subheader("Agent Work History")

    agent_runs = status.get("latest_agent_runs", [])

    if not agent_runs:
        st.info("No agent runs found for this case.")
    else:
        for run in agent_runs:
            agent_name = format_label(run["agent_name"])
            run_status = format_label(run["status"])

            with st.expander(
                f"{agent_name} | {run_status} | {run['created_at']}",
                expanded=False,
            ):
                st.json(run["output_payload"])

except requests.exceptions.ConnectionError:
    st.error(
        "Could not connect to FastAPI backend. Start it with: "
        "uvicorn app.main:app --reload"
    )

except Exception as error:
    st.error(f"Workflow status error: {error}")