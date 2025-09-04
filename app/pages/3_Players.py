import streamlit as st
import os
import sys

_CUR_DIR = os.path.dirname(__file__)
_APP_ROOT = os.path.dirname(_CUR_DIR)
if _APP_ROOT not in sys.path:
    sys.path.insert(0, _APP_ROOT)

try:
    from app import api_client as api
    from app.charts import per90_bar, valuation_trend
    from app.utils import (
        df_from_list,
        empty_state,
        get_list,
        search_select,
        filter_bar,
        inject_theme,
        section_tabs,
    )
except ModuleNotFoundError:
    import api_client as api
    from charts import per90_bar, valuation_trend
    from utils import (
        df_from_list,
        empty_state,
        get_list,
        search_select,
        filter_bar,
        inject_theme,
        section_tabs,
    )


inject_theme()
st.title("Players")
season, competition = filter_bar(
    include_season=True, include_competition=True, key_prefix="player_insights"
)

player_id, _ = search_select(
    label="Player",
    search_fn=api.search_players,
    result_keys=("players", "results"),
    id_keys=("id", "player_id"),
    name_keys=("name", "player_name"),
    key="player_insights_search",
)

if not player_id:
    empty_state("Search and select a player.")
    st.stop()

overall_season_stats = (
    api.player_season(player_id, season) if (season and player_id) else None
)
comp_season_stats = (
    api.player_season_competition(player_id, season, competition)
    if (season and competition and player_id)
    else None
)
career = api.player_career(player_id) if player_id else []
val_season = (
    api.player_valuation_season(player_id, season) if (season and player_id) else None
)
val_hist = api.player_valuation_history(player_id) if player_id else {}

if competition:
    if comp_season_stats is None:
        empty_state(
            "Selected competition has no appearances for this player in the chosen season."
        )
        st.stop()
    season_stats = comp_season_stats
else:
    season_stats = overall_season_stats

comp_name = (
    (season_stats or {}).get("competition_name")
    if isinstance(season_stats, dict)
    else None
)
per90_title = f"Per90 Metrics ({comp_name})" if comp_name else "Per90 Metrics"
tabs = section_tabs(
    ["Per90", "Season Summary", "Career", "Valuation"], key="players_tabs"
)
ps = season_stats or {}


def _to_float(x) -> float:
    try:
        if x is None:
            return 0.0
        if isinstance(x, (int, float)):
            return float(x)
        # Handle numeric strings and comma decimals
        s = str(x).strip().replace(",", ".")
        return float(s)
    except Exception:
        return 0.0


g90 = _to_float(ps.get("goals_per90"))
a90 = _to_float(ps.get("assists_per90"))
ga90 = _to_float(ps.get("goal_plus_assist_per90"))

with tabs[0]:
    st.subheader(per90_title)
    cols = st.columns([1, 2])
    with cols[0]:
        st.metric("Goals/90", f"{g90:.2f}")
        st.metric("Assists/90", f"{a90:.2f}")
        st.metric("G+A/90", f"{ga90:.2f}")
    with cols[1]:
        st.plotly_chart(
            per90_bar(g90, a90, ga90), use_container_width=True, key="players_per90_bar"
        )

with tabs[1]:
    st.subheader("Season Summary")
    cols_sum = st.columns(4)
    with cols_sum[0]:
        st.metric("Games", f"{ps.get('games_played') or 0}")
    with cols_sum[1]:
        st.metric("Minutes", f"{ps.get('minutes_played') or 0}")
    with cols_sum[2]:
        st.metric("Goals", f"{ps.get('goals') or 0}")
    with cols_sum[3]:
        st.metric("Assists", f"{ps.get('assists') or 0}")

with tabs[2]:
    st.subheader("Career Overview")
    try:
        import pandas as _pd

        cdf = _pd.DataFrame(career or [])
        if not cdf.empty:
            total_games = (
                _pd.to_numeric(cdf.get("games_played"), errors="coerce").fillna(0).sum()
            )
            total_minutes = (
                _pd.to_numeric(cdf.get("minutes_played"), errors="coerce")
                .fillna(0)
                .sum()
            )
            total_goals = (
                _pd.to_numeric(cdf.get("goals"), errors="coerce").fillna(0).sum()
            )
            total_assists = (
                _pd.to_numeric(cdf.get("assists"), errors="coerce").fillna(0).sum()
            )
            cols_career = st.columns(4)
            with cols_career[0]:
                st.metric("Total Games", f"{int(total_games)}")
            with cols_career[1]:
                st.metric("Total Minutes", f"{int(total_minutes)}")
            with cols_career[2]:
                st.metric("Total Goals", f"{int(total_goals)}")
            with cols_career[3]:
                st.metric("Total Assists", f"{int(total_assists)}")
        else:
            empty_state("No career history available.")
    except Exception:
        empty_state("Career overview unavailable.")

with tabs[3]:
    st.subheader("Valuation Trend")
vh_items = (
    val_hist
    if isinstance(val_hist, list)
    else (
        get_list(val_hist, key="history")
        or get_list(val_hist, key="valuations")
        or get_list(val_hist, key="timeline")
        or get_list(val_hist, key="seasons")
    )
)
vh_df = df_from_list(vh_items)
if not player_id:
    empty_state("Search a player and press Enter.")
elif vh_df.empty:
    empty_state("No valuation history.")
else:
    cols = set(vh_df.columns)
    if {"date", "value"}.issubset(cols):
        plot_df = vh_df
        x_col, y_col = "date", "value"
    elif "season" in cols:
        for cand in [
            "last_market_value",
            "max_market_value",
            "first_market_value",
            "min_market_value",
            "market_value",
        ]:
            if cand in cols:
                y_sel = cand
                break
        else:
            y_sel = None
        if y_sel is None:
            empty_state("Valuation data missing value columns.")
            plot_df = None
        else:
            plot_df = vh_df[["season", y_sel]].rename(columns={y_sel: "value"}).copy()
            try:
                plot_df["value"] = plot_df["value"].apply(_to_float)
            except Exception:
                pass
        x_col, y_col = "season", "value"
    else:
        plot_df = None
        x_col, y_col = None, None

    if plot_df is not None:
        try:
            if x_col == "date" and "date" in plot_df.columns:
                plot_df = plot_df.sort_values(by="date")
            elif x_col == "season" and "season" in plot_df.columns:
                plot_df = plot_df.sort_values(by="season")
        except Exception:
            pass
        st.plotly_chart(
            valuation_trend(plot_df, x=x_col, y=y_col),
            use_container_width=True,
            key="players_valuation_trend",
        )
    else:
        empty_state("Valuation data format not supported.")
