"""
History page — review past decisions, their chosen options, and any
feedback submitted afterward.
"""

import streamlit as st

st.set_page_config(page_title="History | Decision OS", page_icon="🗂️")
st.title("🗂️ Decision History")

st.caption("Past decisions will be listed here once connected to `GET /decisions/user/{user_id}`.")

placeholder_decisions = [
    {"title": "Which laptop should I buy?", "status": "evaluated", "chosen": "Laptop B"},
    {"title": "Where should we host the offsite?", "status": "pending", "chosen": None},
]

for d in placeholder_decisions:
    with st.container(border=True):
        st.subheader(d["title"])
        st.write(f"Status: `{d['status']}`")
        if d["chosen"]:
            st.write(f"Chosen: **{d['chosen']}**")
            rating = st.slider(
                "How satisfied are you with this outcome?",
                1, 5, 3,
                key=f"rating_{d['title']}",
            )
            if st.button("Submit feedback", key=f"feedback_{d['title']}"):
                st.success("Feedback will be sent to POST /feedback once wired up.")
