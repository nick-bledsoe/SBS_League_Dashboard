import streamlit as st
import base64
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
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown(
        f'<div style="text-align: center"><img src="data:image/png;base64,{base64.b64encode(open("coachSmith.png", "rb").read()).decode()}" width="53"></div>',
        unsafe_allow_html=True
    )
    st.markdown("<h1 style='text-align: center'><em>SBS League Dashboard</em></h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: orange'>2025 quest for the Coach Smith Cup</h3>", unsafe_allow_html=True)

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
