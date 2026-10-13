"""
Profile page — manage account details and view/edit recorded preferences.
"""

import streamlit as st

st.set_page_config(page_title="Profile | Decision OS", page_icon="👤")
st.title("👤 Profile & Preferences")

with st.form("profile_form"):
    st.subheader("Account")
    full_name = st.text_input("Full name")
    email = st.text_input("Email")
    submitted = st.form_submit_button("Save profile")
    if submitted:
        st.success("Profile save wired up once the backend API client is implemented.")

st.divider()

st.subheader("Preferences")
st.caption("Tell Decision OS what matters to you when weighing options.")

col1, col2 = st.columns(2)
with col1:
    category = st.text_input("Category", placeholder="e.g. cost, quality, speed")
with col2:
    weight = st.slider("Importance", min_value=0.0, max_value=1.0, value=0.5, step=0.05)

if st.button("Add preference"):
    st.success(f"Preference '{category}' (weight {weight}) will be saved via the API.")

st.caption("Existing preferences will be listed here once the backend is connected.")
