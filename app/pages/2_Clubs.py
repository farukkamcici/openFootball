import streamlit as st
import os
import sys

_CUR_DIR = os.path.dirname(__file__)
_APP_ROOT = os.path.dirname(_CUR_DIR)
if _APP_ROOT not in sys.path:
    sys.path.insert(0, _APP_ROOT)

try:
    from app import api_client as api
    from app.charts import results_trendline
    from app.utils import (
        df_from_list,
        empty_state,
        kpi_grid,
        filter_bar,
        search_select,
        inject_theme,
        section_tabs,
    )
except ModuleNotFoundError:
    import api_client as api
    from charts import results_trendline
    from utils import (
        df_from_list,
        empty_state,
        kpi_grid,
        filter_bar,
        search_select,
        inject_theme,
        section_tabs,
    )


inject_theme()
st.title("Club Dashboard")
season, competition_id = filter_bar(
    include_season=True, include_competition=True, key_prefix="club_dashboard"
)

club_id, _ = search_select(
    label="Club",
    search_fn=lambda q: api.search_clubs(q),
    result_keys=("clubs", "results"),
    id_keys=("id", "club_id"),
    name_keys=("name", "club_name"),
    key="club_dashboard_search",
)
if not club_id:
    empty_state("Search and select a club.")
    st.stop()

summary_overall = api.club_season(club_id, season) if (club_id and season) else {}
league_split = api.club_league_split(club_id, season) if (club_id and season) else []

comp_slice = None
if competition_id and league_split:
    for r in league_split:
        try:
            if str(r.get("competition_id")) == str(competition_id):
                comp_slice = r
                break
        except Exception:
            continue

tab_summary, tab_history, tab_formations = section_tabs(
    ["Season Summary", "Performance", "Formations"],
    key="clubs_tabs",
)

with tab_summary:
    split_df = df_from_list(league_split)
    if not (club_id and season):
        empty_state("Requires club and season.")
    elif split_df.empty:
        empty_state("No league split data.")
    else:
        st.dataframe(split_df, use_container_width=True, hide_index=True)

with tab_history:
    if competition_id and comp_slice is not None:
        summary = {
            "points": comp_slice.get("points"),
            "wins": comp_slice.get("wins"),
            "draws": comp_slice.get("draws"),
            "losses": comp_slice.get("losses"),
            "goals_for": comp_slice.get("goals_for"),
            "goals_against": comp_slice.get("goals_against"),
        }
        kpi_grid(
            [
                ("Points", str(summary.get("points", "-"))),
                (
                    "W-D-L",
                    f"{summary.get('wins',0)}-{summary.get('draws',0)}-{summary.get('losses',0)}",
                ),
                (
                    "GF/GA",
                    f"{summary.get('goals_for',0)}/{summary.get('goals_against',0)}",
                ),
            ]
        )
    elif competition_id and comp_slice is None:
        empty_state("Club not in selected competition for this season.")

    if competition_id:
        history = api.club_history_competition(club_id, competition_id)
        trend_df = df_from_list(history)
        if not trend_df.empty:
            st.caption("Points trend within selected competition")
            st.plotly_chart(
                results_trendline(trend_df),
                use_container_width=True,
                key="clubs_points_trend",
            )
        else:
            empty_state("Club not in selected competition for this season.")
    else:
        empty_state("Select a competition to view this chart.")

with tab_formations:
    formations = (
        api.club_formations(club_id, season, competition_id)
        if (club_id and season and competition_id)
        else []
    )
    form_df = df_from_list(formations)
    if not (club_id and season and competition_id):
        empty_state("Select club, season and competition to view formations.")
    elif form_df.empty:
        empty_state("No formation data.")
    else:
        st.dataframe(form_df, use_container_width=True, hide_index=True)
