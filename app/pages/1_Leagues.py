import streamlit as st
import os
import sys

_CUR_DIR = os.path.dirname(__file__)
_APP_ROOT = os.path.dirname(_CUR_DIR)
if _APP_ROOT not in sys.path:
    sys.path.insert(0, _APP_ROOT)

try:
    from app import api_client as api
    from app.charts import histogram_goals, scatter_points_vs_gd
    from app.utils import (
        df_from_list,
        empty_state,
        kpi_grid,
        filter_bar,
        get_list,
        inject_theme,
        render_sidebar,
        section_tabs,
    )
except ModuleNotFoundError:
    import api_client as api
    from charts import histogram_goals, scatter_points_vs_gd
    from utils import (
        df_from_list,
        empty_state,
        kpi_grid,
        filter_bar,
        get_list,
        inject_theme,
        render_sidebar,
        section_tabs,
    )


inject_theme()
render_sidebar()
st.title("League Overview")
season, competition_id = filter_bar(
    include_season=True, include_competition=True, key_prefix="league_overview"
)

if not (season and competition_id):
    empty_state("Select a season and competition to view the league.")
    st.stop()

tbl = api.league_table(season, competition_id) or []
stats = api.league_stats(season, competition_id) or {}

club_count = stats.get("club_count", 0)
avg_points = stats.get("avg_points", 0) or 0
avg_gd = stats.get("avg_gd", 0) or 0
total_goals = stats.get("total_goals", 0) or 0

kpi_grid(
    [
        ("Clubs", f"{club_count}"),
        ("Total Goals", f"{total_goals:,}"),
        ("Avg Points", f"{avg_points:.2f}"),
    ]
)

table_df = df_from_list(get_list(tbl) or get_list(tbl, key="table"))

tab_overview, tab_table, tab_scatter, tab_goals = section_tabs(
    ["Overview", "Table", "Points vs GD", "Goals Distribution"],
    key="leagues_tabs",
)

with tab_overview:
    if table_df.empty:
        empty_state("League table unavailable for selected filters.")
    else:
        st.dataframe(table_df.head(10), use_container_width=True, hide_index=True)
        scatter_df = table_df.rename(
            columns={"goal_difference": "gd", "club_name": "club"}
        )
        st.plotly_chart(
            scatter_points_vs_gd(scatter_df),
            use_container_width=True,
            key="scatter_overview",
        )

with tab_table:
    if table_df.empty:
        empty_state("League table unavailable for selected filters.")
    else:
        st.dataframe(table_df, use_container_width=True, hide_index=True)

with tab_scatter:
    if table_df.empty:
        empty_state("No table available.")
    else:
        scatter_df = table_df.rename(
            columns={"goal_difference": "gd", "club_name": "club"}
        )
        st.plotly_chart(
            scatter_points_vs_gd(scatter_df),
            use_container_width=True,
            key="scatter_points_tab",
        )

with tab_goals:
    if table_df.empty or "goals_for" not in table_df.columns:
        empty_state("No goals data.")
    else:
        st.plotly_chart(
            histogram_goals(table_df, column="goals_for"),
            use_container_width=True,
            key="hist_goals_for",
        )
