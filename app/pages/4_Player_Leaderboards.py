import streamlit as st
import pandas as pd
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
        render_sidebar,
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
        render_sidebar,
        section_tabs,
    )


inject_theme()
render_sidebar()
st.title("Player Leaderboards")
season, competition = filter_bar(
    include_season=True, include_competition=True, key_prefix="player_leaderboards"
)

(tab_lb,) = section_tabs(["Leaderboards"], key="leaderboards_tabs")
with tab_lb:
    if season:
        metric = st.selectbox(
            "Metric",
            [
                "goals",
                "assists",
                "total_goals_and_assists",
                "minutes_played",
                "goals_per90",
                "assists_per90",
                "goal_plus_assist_per90",
                "efficiency_score",
            ],
            index=0,
            key="leaderboards_metric",
        )
        min_minutes = st.slider(
            "Min minutes", 0, 3000, 600, 30, key="leaderboards_min_minutes"
        )
        top = api.players_top(
            season,
            metric=metric,
            min_minutes=min_minutes,
            limit=50,
            competition=competition,
        )

        top_df = df_from_list(
            get_list(top)
            or get_list(top, key="players")
            or get_list(top, key="leaders")
        )
        if metric == "total_goals_and_assists" and metric not in top_df.columns:
            if {"goals", "assists"}.issubset(set(top_df.columns)):
                g = pd.to_numeric(top_df["goals"], errors="coerce").fillna(0)
                a = pd.to_numeric(top_df["assists"], errors="coerce").fillna(0)
                top_df[metric] = g + a
        if metric == "goal_plus_assist_per90" and metric not in top_df.columns:
            if {"goals_per90", "assists_per90"}.issubset(set(top_df.columns)):
                g90 = pd.to_numeric(top_df["goals_per90"], errors="coerce").fillna(0)
                a90 = pd.to_numeric(top_df["assists_per90"], errors="coerce").fillna(0)
                top_df[metric] = g90 + a90
        if metric in top_df.columns:
            top_df[metric] = pd.to_numeric(top_df[metric], errors="coerce")
            top_df = top_df.sort_values(by=metric, ascending=False, kind="mergesort")
        if top_df.empty:
            empty_state("No leaderboard data for filters.")
        else:
            st.dataframe(top_df, use_container_width=True, hide_index=True)
    else:
        empty_state("Select a season to view leaderboards.")
