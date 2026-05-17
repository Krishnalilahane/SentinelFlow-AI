import sys
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))

from ui_helpers import case_display_name, format_label, short_id


API_BASE_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="Audit Events | SentinelFlow AI",
    page_icon="📋",
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


st.title("Audit Events")
st.caption("Readable audit trail of case activity and workflow events.")

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

    st.subheader("Selected Case")

    c1, c2, c3, c4 = st.columns(4)

    c1.write("**Status**")
    c1.info(format_label(selected_case["state"]))

    c2.write("**Priority**")
    c2.warning(format_label(selected_case["priority"]))

    c3.write("**Case Type**")
    c3.info(format_label(selected_case["case_type"]))

    c4.write("**Case ID**")
    c4.code(short_id(selected_case["id"]))

    st.divider()

    events = get_case_events(case_id)

    st.subheader("Event Log")

    if not events:
        st.info("No events found for this case.")
    else:
        cleaned_events = []

        for event in events:
            cleaned_events.append(
                {
                    "Time": event.get("created_at"),
                    "Event": format_label(event.get("event_type")),
                    "Details": event.get("message"),
                }
            )

        event_df = pd.DataFrame(cleaned_events)

        st.dataframe(
            event_df,
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("Event Summary")

        event_counts = event_df["Event"].value_counts().reset_index()
        event_counts.columns = ["Event", "Count"]

        st.dataframe(
            event_counts,
            use_container_width=True,
            hide_index=True,
        )

        st.bar_chart(
            event_counts,
            x="Event",
            y="Count",
            use_container_width=True,
        )

except requests.exceptions.ConnectionError:
    st.error(
        "Could not connect to FastAPI backend. Start it with: "
        "uvicorn app.main:app --reload"
    )

except Exception as error:
    st.error(f"Audit events error: {error}")