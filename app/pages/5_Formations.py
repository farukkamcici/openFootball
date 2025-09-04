import streamlit as st

import api_client as api
from utils import df_from_list, empty_state, get_list, filter_bar


st.title("Formations")
season, competition_id = filter_bar(
    include_season=True, include_competition=True, key_prefix="formations"
)

league_forms = (
    api.formations_league(season, competition_id) if season and competition_id else None
)
history = api.formations_history() or {}

st.subheader("League Formation Table")
lf_df = df_from_list(get_list(league_forms, key="formations"))
if not (season and competition_id):
    empty_state("Select season and competition to view league formations.")
elif lf_df.empty:
    empty_state("No league formation data.")
else:
    st.dataframe(lf_df, use_container_width=True, hide_index=True)

st.subheader("Global Formation History")
hist_df = df_from_list(get_list(history, key="history"))
if hist_df.empty:
    empty_state("No historical formation data.")
else:
    st.dataframe(hist_df, use_container_width=True, hide_index=True)
