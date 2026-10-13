"""
Insights page — visualize preference trends and decision statistics
sourced from the analytics API.
"""

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Insights | Decision OS", page_icon="📊")
st.title("📊 Insights")

st.caption("Summary stats will be sourced from GET /analytics/user/{user_id}/summary.")

col1, col2, col3 = st.columns(3)
col1.metric("Total decisions", "—")
col2.metric("Avg. satisfaction", "—")
col3.metric("Top preference", "—")

st.subheader("Preference weight trends")
st.caption("Sourced from GET /analytics/user/{user_id}/preference-trends once implemented.")

# Placeholder chart shape — replace with real data from the API.
sample_df = pd.DataFrame(
    {
        "cost": [0.4, 0.42, 0.38, 0.35],
        "quality": [0.3, 0.31, 0.34, 0.37],
        "speed": [0.3, 0.27, 0.28, 0.28],
    },
    index=["Week 1", "Week 2", "Week 3", "Week 4"],
)
st.line_chart(sample_df)
