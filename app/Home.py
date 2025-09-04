import streamlit as st


st.set_page_config(
    page_title="OpenFootball Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.title("OpenFootball Analytics")
st.markdown("Select filters from each page’s top filter bar.")

st.divider()
st.markdown("#### Quick Links")
st.write(
    "- League Overview\n- Club Dashboard\n- Players\n- Market Movers\n- Formations\n- Managers\n- Transfers"
)
