import streamlit as st
import os
import sys

_CUR_DIR = os.path.dirname(__file__)
_APP_ROOT = os.path.dirname(_CUR_DIR)
if _APP_ROOT not in sys.path:
    sys.path.insert(0, _APP_ROOT)

try:
    from app import api_client as api
    from app.utils import (
        df_from_list,
        empty_state,
        get_list,
        filter_bar,
        inject_theme,
        section_tabs,
    )
except ModuleNotFoundError:
    import api_client as api
    from utils import (
        df_from_list,
        empty_state,
        get_list,
        filter_bar,
        inject_theme,
        section_tabs,
    )


inject_theme()
st.title("Formations")
season, competition_id = filter_bar(
    include_season=True, include_competition=True, key_prefix="formations"
)

league_forms = (
    api.formations_league(season, competition_id) if season and competition_id else None
)
history = api.formations_history() or {}

tab_league, tab_history = section_tabs(
    ["League Table", "Global History"], key="formations_tabs"
)

with tab_league:
    lf_df = df_from_list(get_list(league_forms, key="formations"))
    if not (season and competition_id):
        empty_state("Select season and competition to view league formations.")
    elif lf_df.empty:
        empty_state("No league formation data.")
    else:
        st.dataframe(lf_df, use_container_width=True, hide_index=True)

with tab_history:
    hist_df = df_from_list(get_list(history, key="history"))
    if hist_df.empty:
        empty_state("No historical formation data.")
    else:
        st.dataframe(hist_df, use_container_width=True, hide_index=True)
