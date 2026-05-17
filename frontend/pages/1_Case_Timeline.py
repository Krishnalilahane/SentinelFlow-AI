import sys
from pathlib import Path

import requests
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))

from ui_helpers import case_display_name, format_label, short_id

API_BASE_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="Case Timeline | SentinelFlow AI",
    page_icon="🧾",
    layout="wide",
)


def get_cases() -> list[dict]:
    response = requests.get(f"{API_BASE_URL}/cases", timeout=15)
    response.raise_for_status()
    return response.json()


def get_case_events(case_id: str) -> list[dict]:
    response = requests.get(f"{API_BASE_URL}/cases/{case_id}/events", timeout=15)
    response.raise_for_status()
    return response.json()


st.title("Case Timeline")
st.caption("Simple view of what happened in a case, step by step.")

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

    st.subheader("Case Summary")

    col1, col2, col3, col4 = st.columns(4)

    col1.write("**Status**")
    col1.info(format_label(selected_case["state"]))

    col2.write("**Priority**")
    col2.warning(format_label(selected_case["priority"]))

    col3.write("**Case Type**")
    col3.info(format_label(selected_case["case_type"]))

    col4.write("**Case ID**")
    col4.code(short_id(selected_case["id"]))

    st.write("**Customer ID:**", short_id(selected_case["customer_id"], 14))
    st.write("**Transaction ID:**", short_id(selected_case["transaction_id"], 14))
    st.write("**Description:**", selected_case["description"])
    st.write("**Created:**", selected_case["created_at"])
    st.write("**Last Updated:**", selected_case["updated_at"])

    st.divider()

    st.subheader("Timeline")

    events = get_case_events(case_id)

    if not events:
        st.info("No events found for this case.")
    else:
        for event in events:
            with st.container(border=True):
                st.write(f"**{format_label(event['event_type'])}**")
                st.write(event["message"])
                st.caption(event["created_at"])

except requests.exceptions.ConnectionError:
    st.error(
        "Could not connect to FastAPI backend. Start it with: "
        "uvicorn app.main:app --reload"
    )

except Exception as error:
    st.error(f"Case timeline error: {error}")