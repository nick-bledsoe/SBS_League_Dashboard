import streamlit as st
from page_home import render_home_tab
from page_teams import render_teams_tab
from page_playoffs import render_playoffs_tab

# Page configuration
st.set_page_config(
    page_title="SBS League Dash",
    page_icon="coachSmith.png",
    layout="wide"
)

# Header
col1, col2 = st.columns([10, 1])
with col1:
    st.title("_SBS League Dashboard_")
    st.subheader(":orange[2025 quest for the Coach Smith Cup]")
with col2:
    st.image("coachSmith.png", width=53)

# Navigation tabs
tab1, tab2, tab3 = st.tabs(["Home", "Teams", "Playoffs"])

# HOME TAB
with tab1:
    render_home_tab()

# TEAMS TAB
with tab2:
    render_teams_tab()

# PLAYOFFS TAB
with tab3:
    render_playoffs_tab()

# Footer
st.caption("_Data sourced from ESPN Fantasy Football API - Created by Nick Bledsoe (2025)_")
