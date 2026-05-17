import pandas as pd
import streamlit as st

from api_client import APIError, check_db_health, check_health, list_cases
from ui_helpers import configure_page, page_header, show_api_error, workflow_stage_map

configure_page("Executive Overview")

page_header(
    "SentinelFlow AI",
    "Enterprise Multi-Agent FinTech RiskOps Orchestrator",
)

st.write(
    """
SentinelFlow AI uses RAG, LangGraph multi-agent workflows, PostgreSQL persistence,
risk scoring, human-in-the-loop review, and audit logging to process fintech risk cases.
This website is the frontend control layer for demonstrating the AI orchestration system.
"""
)

st.subheader("System Health")

try:
    health = check_health()
    db_health = check_db_health()
    cases = list_cases()

    total_cases = len(cases)
    pending_human_review = len(
        [case for case in cases if case.get("state") == "WAITING_FOR_HUMAN"]
    )
    closed_cases = len([case for case in cases if case.get("state") == "CLOSED"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Backend Status", str(health.get("status", "unknown")).upper())
    col2.metric("Database", str(db_health.get("database", "unknown")).upper())
    col3.metric("Total Cases", total_cases)
    col4.metric("Pending Human Review", pending_human_review)

    col5, col6 = st.columns(2)
    col5.metric("Closed Cases", closed_cases)
    col6.metric("Backend Service", health.get("service", "sentinelflow-api"))

except APIError as exc:
    show_api_error(exc)
    cases = []

st.divider()

st.subheader("AI Workflow")

st.code(
    "Case Intake → RAG Policy Search → Risk Analysis → Decision Recommendation → Human Review → Audit Trail",
    language="text",
)

st.write(
    """
The system demonstrates a deterministic enterprise AI workflow. A case is created,
policy evidence is retrieved, risk is analysed, a decision is recommended, high-risk
cases are routed to human review, and every major action is captured in the audit trail.
"""
)

workflow_df = pd.DataFrame(workflow_stage_map())
st.dataframe(workflow_df, use_container_width=True, hide_index=True)

st.divider()

st.subheader("System Components")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown("**FastAPI**")
    st.caption("Backend API layer")

with col2:
    st.markdown("**PostgreSQL**")
    st.caption("Case persistence")

with col3:
    st.markdown("**RAG**")
    st.caption("Policy evidence retrieval")

with col4:
    st.markdown("**LangGraph**")
    st.caption("Deterministic agent workflow")

with col5:
    st.markdown("**Streamlit**")
    st.caption("Portfolio website layer")

st.divider()

st.subheader("Website Navigation")

st.write(
    """
Use the pages in the sidebar to create a risk case, run the AI workflow,
inspect agent reasoning, search policy evidence, complete human review,
view the audit timeline, and monitor operational metrics.
"""
)

if cases:
    st.subheader("Recent Cases")
    preview = pd.DataFrame(cases).head(10)
    useful_cols = [
        col
        for col in ["id", "customer_id", "case_type", "priority", "state", "created_at"]
        if col in preview.columns
    ]
    st.dataframe(preview[useful_cols], use_container_width=True, hide_index=True)
else:
    st.info("No cases available yet.")