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
    ["Career", "Season", "Value vs Performance"],
    key="players_tabs",
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
    st.subheader("Career")
    # Career totals
    try:
        import pandas as _pd

        cdf_over = _pd.DataFrame(career or [])
        if not cdf_over.empty:
            total_games = (
                _pd.to_numeric(cdf_over.get("games_played"), errors="coerce")
                .fillna(0)
                .sum()
            )
            total_minutes = (
                _pd.to_numeric(cdf_over.get("minutes_played"), errors="coerce")
                .fillna(0)
                .sum()
            )
            total_goals = (
                _pd.to_numeric(cdf_over.get("goals"), errors="coerce").fillna(0).sum()
            )
            total_assists = (
                _pd.to_numeric(cdf_over.get("assists"), errors="coerce").fillna(0).sum()
            )
        else:
            total_games = total_minutes = total_goals = total_assists = 0
    except Exception:
        total_games = total_minutes = total_goals = total_assists = 0

    top = st.columns(4)
    with top[0]:
        st.metric("Career Games", f"{int(total_games)}")
    with top[1]:
        st.metric("Career Minutes", f"{int(total_minutes)}")
    with top[2]:
        st.metric("Career Goals", f"{int(total_goals)}")
    with top[3]:
        st.metric("Career Assists", f"{int(total_assists)}")

    # Improved valuation chart with seasons
    st.subheader("Valuation by Season")
    try:
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
        vdf = df_from_list(vh_items)
        plot_df = None
        if not vdf.empty:
            if "season" in vdf.columns:
                for cand in [
                    "last_market_value",
                    "max_market_value",
                    "first_market_value",
                    "min_market_value",
                    "market_value",
                    "value",
                ]:
                    if cand in vdf.columns:
                        sel = cand
                        break
                else:
                    sel = None
                if sel:
                    plot_df = vdf[["season", sel]].rename(columns={sel: "value"}).copy()
        if plot_df is not None and not plot_df.empty:
            st.plotly_chart(
                valuation_trend(plot_df, x="season", y="value", title=None),
                use_container_width=True,
                key="players_overview_valuation_season",
            )
        else:
            empty_state("No valuation data.")
    except Exception:
        empty_state("Valuation overview unavailable.")

with tabs[1]:
    st.subheader("Season")
    cols_sum = st.columns(4)
    with cols_sum[0]:
        st.metric("Games", f"{ps.get('games_played') or 0}")
    with cols_sum[1]:
        st.metric("Minutes", f"{ps.get('minutes_played') or 0}")
    with cols_sum[2]:
        st.metric("Goals", f"{ps.get('goals') or 0}")
    with cols_sum[3]:
        st.metric("Assists", f"{ps.get('assists') or 0}")
    st.markdown("")
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

with tabs[2]:
    st.subheader("Value vs Performance")
    # Side-by-side selectors (slightly larger)
    sel_cols = st.columns([3, 3, 6])
    with sel_cols[0]:
        perf_metric = st.selectbox(
            "Performance",
            ["G+A", "G+A/90", "Goals/90", "Assists/90", "Efficiency"],
            index=0,
            key="players_perf_metric",
        )
    with sel_cols[1]:
        value_metric = st.selectbox(
            "Value",
            ["Last value", "Max value", "YoY delta", "YoY %"],
            index=0,
            key="players_value_metric",
        )

    # Rebuild valuation items for this tab
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
    # Ensure pandas is available in this scope
    try:
        import pandas as _pd
    except Exception:
        pass
    # Import chart helper
    try:
        from app.charts import value_vs_performance_dual
    except ModuleNotFoundError:
        from charts import value_vs_performance_dual
    # Build performance per season: Goals + Assists (robust to missing columns)
    try:
        cdf = _pd.DataFrame(career or [])
        if not cdf.empty and "season" in cdf.columns:
            # Prepare numeric columns
            cdf_nums = cdf.assign(
                goals=_pd.to_numeric(cdf.get("goals"), errors="coerce").fillna(0),
                assists=_pd.to_numeric(cdf.get("assists"), errors="coerce").fillna(0),
                goals_per90=_pd.to_numeric(
                    cdf.get("goals_per90"), errors="coerce"
                ).fillna(0),
                assists_per90=_pd.to_numeric(
                    cdf.get("assists_per90"), errors="coerce"
                ).fillna(0),
                goal_plus_assist_per90=_pd.to_numeric(
                    cdf.get("goal_plus_assist_per90"), errors="coerce"
                ).fillna(0),
                efficiency_score=_pd.to_numeric(
                    cdf.get("efficiency_score"), errors="coerce"
                ).fillna(0),
            )

            if perf_metric == "G+A":
                perf_df = (
                    cdf_nums.groupby("season", as_index=False)[["goals", "assists"]]
                    .sum()
                    .assign(performance=lambda d: d["goals"] + d["assists"])[
                        ["season", "performance"]
                    ]
                )
            elif perf_metric == "G+A/90":
                perf_df = (
                    cdf_nums.groupby("season", as_index=False)[
                        ["goal_plus_assist_per90"]
                    ]
                    .mean()
                    .rename(columns={"goal_plus_assist_per90": "performance"})
                )
            elif perf_metric == "Goals/90":
                perf_df = (
                    cdf_nums.groupby("season", as_index=False)[["goals_per90"]]
                    .mean()
                    .rename(columns={"goals_per90": "performance"})
                )
            elif perf_metric == "Assists/90":
                perf_df = (
                    cdf_nums.groupby("season", as_index=False)[["assists_per90"]]
                    .mean()
                    .rename(columns={"assists_per90": "performance"})
                )
            else:  # Efficiency
                perf_df = (
                    cdf_nums.groupby("season", as_index=False)[["efficiency_score"]]
                    .mean()
                    .rename(columns={"efficiency_score": "performance"})
                )

            # Normalize season to "YYYY/YYYY+1" to align with valuation seasons
            try:
                if not perf_df.empty:
                    perf_df["season"] = (
                        perf_df["season"].astype(int).apply(lambda y: f"{y}/{y+1}")
                    )
            except Exception:
                pass
        else:
            perf_df = _pd.DataFrame(columns=["season", "performance"])  # empty
    except Exception:
        perf_df = _pd.DataFrame(columns=["season", "performance"])  # empty

    # Fallback: if empty, but current season stats available, create single-row perf
    try:
        if perf_df.empty and season and isinstance(ps, dict):
            # Single-season fallback using season-level stats
            if perf_metric == "G+A":
                g = (
                    _pd.to_numeric(ps.get("goals"), errors="coerce")
                    if ps.get("goals") is not None
                    else 0
                )
                a = (
                    _pd.to_numeric(ps.get("assists"), errors="coerce")
                    if ps.get("assists") is not None
                    else 0
                )
                val = (0 if _pd.isna(g) else float(g)) + (
                    0 if _pd.isna(a) else float(a)
                )
            elif perf_metric == "G+A/90":
                val = _pd.to_numeric(ps.get("goal_plus_assist_per90"), errors="coerce")
            elif perf_metric == "Goals/90":
                val = _pd.to_numeric(ps.get("goals_per90"), errors="coerce")
            elif perf_metric == "Assists/90":
                val = _pd.to_numeric(ps.get("assists_per90"), errors="coerce")
            else:
                val = _pd.to_numeric(ps.get("efficiency_score"), errors="coerce")
            val = 0 if _pd.isna(val) else float(val)
            perf_df = _pd.DataFrame({"season": [season], "performance": [val]})
            # Normalize single-season fallback as well
            try:
                perf_df["season"] = (
                    perf_df["season"].astype(int).apply(lambda y: f"{y}/{y+1}")
                )
            except Exception:
                pass
    except Exception:
        pass

    # Build valuation per season (selectable metric; robust to different schemas)
    try:
        vdf = _pd.DataFrame(vh_items or [])
        if not vdf.empty:
            if "season" in vdf.columns:
                value_candidates = [
                    "last_market_value",
                    "max_market_value",
                    "first_market_value",
                    "min_market_value",
                    "market_value",
                    "value",
                ]

                def _choose_col(pref: str) -> str | None:
                    if pref in vdf.columns:
                        return pref
                    return next((c for c in value_candidates if c in vdf.columns), None)

                if value_metric == "Last value":
                    sel = _choose_col("last_market_value")
                    val_season_df = (
                        vdf[["season", sel]].rename(columns={sel: "value"}).copy()
                        if sel
                        else _pd.DataFrame(columns=["season", "value"])  # empty
                    )
                elif value_metric == "Max value":
                    sel = _choose_col("max_market_value")
                    val_season_df = (
                        vdf[["season", sel]].rename(columns={sel: "value"}).copy()
                        if sel
                        else _pd.DataFrame(columns=["season", "value"])  # empty
                    )
                else:
                    # YoY metrics based on 'last_market_value' by default
                    base = _choose_col("last_market_value")
                    base_df = (
                        vdf[["season", base]].rename(columns={base: "value"}).copy()
                        if base
                        else _pd.DataFrame(columns=["season", "value"])  # empty
                    )
                    if not base_df.empty:
                        # Sort by first year of season
                        import re

                        def _year_key(s: str) -> int:
                            m = re.search(r"(19|20)\d{2}", str(s))
                            return int(m.group(0)) if m else 0

                        base_df = base_df.sort_values(
                            by="season", key=lambda s: s.map(_year_key)
                        )
                        base_df["value"] = _pd.to_numeric(
                            base_df["value"], errors="coerce"
                        ).fillna(0)
                        if value_metric == "YoY delta":
                            base_df["value"] = base_df["value"].diff().fillna(0)
                        else:  # YoY %
                            base_df["value"] = (
                                base_df["value"].pct_change().fillna(0) * 100
                            )
                    val_season_df = base_df
            elif {"date", "value"}.issubset(vdf.columns):
                tmp = vdf.copy()
                tmp["date"] = _pd.to_datetime(tmp["date"], errors="coerce")

                # Map date to season like 2019/20 assuming season starts in July
                def _season_label(dt: _pd.Timestamp) -> str:
                    if _pd.isna(dt):
                        return ""
                    y = int(dt.year)
                    start = y if dt.month >= 7 else y - 1
                    return f"{start}/{start+1}"

                tmp["season"] = tmp["date"].apply(_season_label)
                base_df = (
                    tmp.dropna(subset=["season"])
                    .sort_values(["season", "date"])
                    .groupby("season", as_index=False)["value"]
                    .last()
                )
                if value_metric in ("YoY delta", "YoY %") and not base_df.empty:
                    import re

                    def _year_key(s: str) -> int:
                        m = re.search(r"(19|20)\d{2}", str(s))
                        return int(m.group(0)) if m else 0

                    base_df = base_df.sort_values(
                        by="season", key=lambda s: s.map(_year_key)
                    )
                    base_df["value"] = _pd.to_numeric(
                        base_df["value"], errors="coerce"
                    ).fillna(0)
                    if value_metric == "YoY delta":
                        base_df["value"] = base_df["value"].diff().fillna(0)
                    else:
                        base_df["value"] = base_df["value"].pct_change().fillna(0) * 100
                val_season_df = base_df
            else:
                val_season_df = _pd.DataFrame(columns=["season", "value"])  # empty
        else:
            val_season_df = _pd.DataFrame(columns=["season", "value"])  # empty
    except Exception:
        val_season_df = _pd.DataFrame(columns=["season", "value"])  # empty

    try:
        combined = _pd.merge(val_season_df, perf_df, on="season", how="outer")
        # Drop empty/blank seasons
        combined = combined[combined["season"].astype(str).str.len() > 0]
        if not combined.empty:
            for col in ["value", "performance"]:
                combined[col] = _pd.to_numeric(combined[col], errors="coerce").fillna(0)
            st.plotly_chart(
                value_vs_performance_dual(
                    combined,
                    x_col="season",
                    value_col="value",
                    perf_col="performance",
                    value_name=value_metric,
                    perf_name=perf_metric,
                ),
                use_container_width=True,
                key="players_value_perf_dual",
            )
        else:
            empty_state("Not enough data for value vs performance.")
    except Exception:
        empty_state("Value vs performance chart unavailable.")
