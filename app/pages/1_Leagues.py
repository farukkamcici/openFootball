import streamlit as st

import api_client as api
from charts import histogram_goals, scatter_points_vs_gd
from utils import df_from_list, empty_state, kpi_grid, filter_bar, get_list


st.title("League Overview")
season, competition_id = filter_bar(
    include_season=True, include_competition=True, key_prefix="league_overview"
)

if not (season and competition_id):
    empty_state("Select a season and competition to view the league.")
    st.stop()

# Only fetch when both filters are present
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
st.subheader("Table")
if table_df.empty:
    empty_state("League table unavailable for selected filters.")
else:
    st.dataframe(table_df, use_container_width=True, hide_index=True)

st.subheader("Points vs Goal Difference")
if table_df.empty:
    empty_state("No table available.")
else:
    scatter_df = table_df.rename(columns={"goal_difference": "gd", "club_name": "club"})
    st.plotly_chart(scatter_points_vs_gd(scatter_df), use_container_width=True)

st.subheader("Goals For Distribution")
if table_df.empty or "goals_for" not in table_df.columns:
    empty_state("No goals data.")
else:
    st.plotly_chart(
        histogram_goals(table_df, column="goals_for"), use_container_width=True
    )
