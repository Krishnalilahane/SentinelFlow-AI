import json
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st


def configure_page(title: str) -> None:
    st.set_page_config(
        page_title=f"{title} | SentinelFlow AI",
        page_icon=None,
        layout="wide",
        initial_sidebar_state="expanded",
    )


def page_header(title: str, subtitle: Optional[str] = None) -> None:
    st.title(title)
    if subtitle:
        st.caption(subtitle)
    st.divider()


def status_badge(label: str, value: Any) -> None:
    text = str(value).upper() if value is not None else "UNKNOWN"

    if text in {"OK", "CONNECTED", "CLOSED", "APPROVED", "COMPLETED"}:
        st.success(f"{label}: {text}")
    elif text in {"WAITING_FOR_HUMAN", "PENDING", "ESCALATED", "HIGH", "CRITICAL"}:
        st.warning(f"{label}: {text}")
    elif text in {"FAILED", "ERROR", "REJECTED"}:
        st.error(f"{label}: {text}")
    else:
        st.info(f"{label}: {text}")


def show_api_error(error: Exception) -> None:
    st.error(str(error))
    st.info("Check that Docker, PostgreSQL, and FastAPI are running before using this page.")


def safe_json_block(title: str, data: Any) -> None:
    with st.expander(title, expanded=False):
        if data is None:
            st.write("No data available.")
            return

        if isinstance(data, (dict, list)):
            st.json(data)
            return

        try:
            parsed = json.loads(data)
            st.json(parsed)
        except Exception:
            st.write(data)


def case_label(case: Dict[str, Any]) -> str:
    case_id = case.get("id", "unknown")
    case_type = case.get("case_type", "UNKNOWN")
    priority = case.get("priority", "UNKNOWN")
    state = case.get("state", "UNKNOWN")
    short_id = str(case_id)[:8]
    return f"{short_id} | {case_type} | {priority} | {state}"


def select_case(cases: List[Dict[str, Any]], label: str = "Select case") -> Optional[Dict[str, Any]]:
    if not cases:
        st.warning("No cases found. Create a risk case first.")
        return None

    selected = st.selectbox(
        label,
        options=cases,
        format_func=case_label,
    )
    return selected


def show_case_summary(case: Dict[str, Any]) -> None:
    if not case:
        st.warning("No case selected.")
        return

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Case Type", case.get("case_type", "N/A"))
    col2.metric("Priority", case.get("priority", "N/A"))
    col3.metric("State", case.get("state", "N/A"))
    col4.metric("Customer", case.get("customer_id", "N/A"))

    st.write("**Case ID:**", case.get("id", "N/A"))
    st.write("**Transaction ID:**", case.get("transaction_id", "N/A"))
    st.write("**Description:**")
    st.write(case.get("description", "No description available."))


def dataframe_from_records(records: List[Dict[str, Any]]) -> pd.DataFrame:
    if not records:
        return pd.DataFrame()
    return pd.DataFrame(records)


def workflow_stage_map() -> List[Dict[str, str]]:
    return [
        {
            "Stage": "1. Case Intake",
            "System Component": "FastAPI + PostgreSQL",
            "Purpose": "Create and persist a fintech risk case.",
        },
        {
            "Stage": "2. RAG Policy Search",
            "System Component": "ChromaDB + Policy Retrieval",
            "Purpose": "Retrieve policy evidence relevant to the case.",
        },
        {
            "Stage": "3. Risk Analysis",
            "System Component": "Risk Analysis Agent",
            "Purpose": "Assess customer, transaction, and policy signals.",
        },
        {
            "Stage": "4. Decision Recommendation",
            "System Component": "Decision Agent",
            "Purpose": "Recommend close, approve, reject, or escalate.",
        },
        {
            "Stage": "5. Human Review",
            "System Component": "Human-in-the-loop Workflow",
            "Purpose": "Route high-risk cases to a reviewer.",
        },
        {
            "Stage": "6. Audit Trail",
            "System Component": "Event Logging",
            "Purpose": "Record traceable workflow events for governance.",
        },
    ]