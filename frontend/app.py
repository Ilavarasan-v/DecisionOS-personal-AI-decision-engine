"""
Decision OS — Streamlit frontend entrypoint.

Run locally with:
    streamlit run app.py
"""

import streamlit as st

st.set_page_config(
    page_title="Decision OS",
    page_icon="🧭",
    layout="wide",
)

st.title("🧭 Decision OS")
st.caption("An AI-assisted decision engine that learns your preferences.")

st.markdown(
    """
    Use the sidebar to navigate:

    - **Profile** — manage your account and preferences
    - **Decision** — create a new decision and get a recommendation
    - **History** — review past decisions and their outcomes
    - **Insights** — see trends in how your preferences shift over time
    """
)

st.info(
    "This is the app shell. Pages under `frontend/pages/` connect to the "
    "FastAPI backend (see `backend/app/main.py`) once it's running."
)
