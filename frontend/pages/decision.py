"""
Decision page — create a new decision, add candidate options, and
trigger the scoring/explanation pipeline.
"""

import streamlit as st

st.set_page_config(page_title="New Decision | Decision OS", page_icon="⚖️")
st.title("⚖️ New Decision")

title = st.text_input("What are you deciding?", placeholder="e.g. Which laptop should I buy?")
description = st.text_area("Any extra context? (optional)")

st.subheader("Options")
if "option_count" not in st.session_state:
    st.session_state.option_count = 2

options = []
for i in range(st.session_state.option_count):
    with st.expander(f"Option {i + 1}", expanded=True):
        name = st.text_input("Name", key=f"opt_name_{i}")
        notes = st.text_area("Notes", key=f"opt_notes_{i}", height=80)
        options.append({"name": name, "notes": notes})

col1, col2 = st.columns(2)
with col1:
    if st.button("➕ Add another option"):
        st.session_state.option_count += 1
        st.rerun()
with col2:
    if st.button("✅ Evaluate decision", type="primary"):
        if not title or not any(o["name"] for o in options):
            st.error("Add a title and at least one named option before evaluating.")
        else:
            st.success(
                "Ready to send to the backend's /decisions and /decisions/{id}/evaluate "
                "endpoints once the API client is wired up."
            )
            st.json({"title": title, "description": description, "options": options})
