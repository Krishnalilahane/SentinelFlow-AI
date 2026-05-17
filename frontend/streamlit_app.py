import pandas as pd
import requests
import streamlit as st

from ui_helpers import format_label, format_number


API_BASE_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="SentinelFlow AI Dashboard",
    page_icon="🛡️",
    layout="wide",
)


def get_metrics() -> dict:
    response = requests.get(f"{API_BASE_URL}/operations/metrics", timeout=15)
    response.raise_for_status()
    return response.json()


st.title("SentinelFlow AI")
st.caption("AI-powered risk operations platform for financial case review")

st.markdown(
    """
SentinelFlow AI helps manage financial risk cases such as suspicious transactions,
chargebacks, KYC reviews, AML alerts, failed payments, and customer complaints.

It demonstrates how AI agents, policy retrieval, risk scoring, human review,
and durable workflow recovery can work together in an enterprise-style system.
"""
)

st.divider()

try:
    metrics = get_metrics()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Cases", metrics["total_cases"])
    col2.metric("Needs Human Review", metrics["human_review_pending_count"])
    col3.metric("Closed Cases", metrics["closed_cases_count"])
    col4.metric("High Risk Cases", metrics["high_or_critical_risk_count"])

    st.subheader("Case Status Overview")

    case_state_data = {
        format_label(state): count
        for state, count in metrics["cases_by_state"].items()
    }

    case_state_df = pd.DataFrame(
        list(case_state_data.items()),
        columns=["Case Status", "Number of Cases"],
    )

    st.dataframe(
        case_state_df,
        use_container_width=True,
        hide_index=True,
    )

    st.bar_chart(
        case_state_df,
        x="Case Status",
        y="Number of Cases",
        use_container_width=True,
    )

    st.subheader("Workflow Activity")

    col5, col6, col7 = st.columns(3)

    col5.metric("Agent Runs Completed", metrics["total_agent_runs"])
    col6.metric("Workflow Events Logged", metrics["total_workflow_events"])

    avg_confidence = metrics["average_confidence_score"]
    col7.metric(
        "Average AI Confidence",
        format_number(avg_confidence),
    )

    st.success("Dashboard connected successfully to the SentinelFlow AI backend.")

except requests.exceptions.ConnectionError:
    st.error(
        "Could not connect to FastAPI backend. Start it with: "
        "uvicorn app.main:app --reload"
    )

except Exception as error:
    st.error(f"Dashboard error: {error}")