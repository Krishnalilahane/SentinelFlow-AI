import streamlit as st

from api_client import APIError, create_case
from ui_helpers import configure_page, page_header, show_api_error, status_badge


configure_page("Create Risk Case")

page_header(
    "Create Risk Case",
    "Create a fintech risk case without using Swagger.",
)

st.write(
    """
Use this page to create a new risk case. The case is sent to the FastAPI backend
and persisted in PostgreSQL. After creation, it can be processed through the
SentinelFlow AI workflow.
"""
)

CASE_TYPES = [
    "SUSPICIOUS_TRANSACTION",
    "CHARGEBACK_DISPUTE",
    "KYC_DOCUMENT_REVIEW",
    "AML_ESCALATION",
    "FAILED_PAYMENT_INVESTIGATION",
    "CUSTOMER_COMPLAINT",
    "LOAN_AFFORDABILITY_REVIEW",
    "ACCOUNT_TAKEOVER_RISK",
]

PRIORITIES = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


if "case_form" not in st.session_state:
    st.session_state.case_form = {
        "customer_id": "",
        "transaction_id": "",
        "case_type": "SUSPICIOUS_TRANSACTION",
        "description": "",
        "priority": "HIGH",
    }


if st.button("Load suspicious transaction example"):
    st.session_state.case_form = {
        "customer_id": "CUST-1001",
        "transaction_id": "TXN-9001",
        "case_type": "SUSPICIOUS_TRANSACTION",
        "description": (
            "Customer reports an unknown card transaction of €487.20 after "
            "three failed login attempts and a new device login yesterday."
        ),
        "priority": "HIGH",
    }
    st.rerun()


with st.form("create_case_form"):
    customer_id = st.text_input(
        "Customer ID",
        value=st.session_state.case_form["customer_id"],
        placeholder="Example: CUST-1001",
    )

    transaction_id = st.text_input(
        "Transaction ID",
        value=st.session_state.case_form["transaction_id"],
        placeholder="Example: TXN-9001",
    )

    case_type = st.selectbox(
        "Case Type",
        CASE_TYPES,
        index=CASE_TYPES.index(st.session_state.case_form["case_type"]),
    )

    priority = st.selectbox(
        "Priority",
        PRIORITIES,
        index=PRIORITIES.index(st.session_state.case_form["priority"]),
    )

    description = st.text_area(
        "Case Description",
        value=st.session_state.case_form["description"],
        height=140,
        placeholder="Describe the risk event, customer issue, transaction behaviour, or escalation reason.",
    )

    submitted = st.form_submit_button("Create Risk Case")

if submitted:
    payload = {
        "customer_id": customer_id.strip(),
        "transaction_id": transaction_id.strip(),
        "case_type": case_type,
        "description": description.strip(),
        "priority": priority,
    }

    missing_fields = [
        field for field, value in payload.items()
        if isinstance(value, str) and not value.strip()
    ]

    if missing_fields:
        st.error(f"Missing required fields: {', '.join(missing_fields)}")
    else:
        try:
            result = create_case(payload)

            st.success("Risk case created successfully.")

            col1, col2, col3 = st.columns(3)
            col1.metric("Case ID", result.get("id", "N/A")[:8])
            col2.metric("Priority", result.get("priority", "N/A"))
            col3.metric("State", result.get("state", "N/A"))

            st.write("**Full Case ID:**", result.get("id", "N/A"))
            status_badge("Current State", result.get("state", "UNKNOWN"))

            with st.expander("Created Case Payload", expanded=True):
                st.json(result)

            st.info("Next step: open the Run AI Workflow page and process this case.")

        except APIError as exc:
            show_api_error(exc)