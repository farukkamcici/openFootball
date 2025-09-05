import streamlit as st
import os
import sys

# Ensure the app root is importable when running from project root
_CUR_DIR = os.path.dirname(__file__)
if _CUR_DIR not in sys.path:
    sys.path.insert(0, _CUR_DIR)

try:
    from utils import inject_theme
except ModuleNotFoundError:
    from app.utils import inject_theme


st.set_page_config(
    page_title="OpenFootball",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Global cosmetic tweaks
inject_theme()

# Hero
cols = st.columns([1, 2])
with cols[0]:
    st.markdown("### ⚽ OpenFootball Analytics")
    st.caption("Explore leagues, clubs, players, market trends and more.")
with cols[1]:
    st.markdown("")

st.divider()

st.markdown("#### Quick Links")
gl = st.columns(3)
with gl[0]:
    st.page_link("pages/1_Leagues.py", label="🏆 League Overview")
    st.page_link("pages/2_Clubs.py", label="🏟️ Club Dashboard")
    st.page_link("pages/5_Formations.py", label="🧩 Formations")
with gl[1]:
    st.page_link("pages/3_Players.py", label="👤 Players")
    st.page_link("pages/4_Player_Leaderboards.py", label="📈 Player Leaderboards")
    st.page_link("pages/6_Managers.py", label="🧠 Managers")
with gl[2]:
    st.page_link("pages/8_Market_Movers.py", label="💹 Market Movers")
    st.page_link("pages/7_Transfers.py", label="🔄 Transfers")
    st.page_link("pages/9_Compare.py", label="🆚 Compare")

st.divider()

st.markdown("#### Tips")
st.caption(
    "Use the filter bars at the top of each page to refine season and competition."
)
