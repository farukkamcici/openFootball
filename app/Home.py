import streamlit as st
import os
import sys
from typing import Any, List, Optional

_CUR_DIR = os.path.dirname(__file__)
if _CUR_DIR not in sys.path:
    sys.path.insert(0, _CUR_DIR)

try:
    from utils import inject_theme, get_list
    import api_client as api
except ModuleNotFoundError:
    from app.utils import inject_theme, get_list
    from app import api_client as api


st.set_page_config(
    page_title="OpenFootball",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_theme()


def _season_labels(payload: Any) -> List[str]:
    items = get_list(payload, key="seasons") or get_list(payload)
    out: List[str] = []
    for it in items:
        if isinstance(it, dict):
            for k in ("season", "year", "name", "label", "code", "id"):
                if k in it and it[k] is not None:
                    out.append(str(it[k]))
                    break
        else:
            out.append(str(it))
    seen = set()
    uniq = []
    for s in out:
        if s not in seen:
            seen.add(s)
            uniq.append(s)
    return uniq


def _latest_season_label(labels: List[str]) -> Optional[str]:
    if not labels:
        return None

    def _start_year(s: str) -> int:
        import re

        try:
            m = re.search(r"(19|20)\d{2}", s)
            return int(m.group(0)) if m else int(float(s))
        except Exception:
            return 0

    return max(labels, key=_start_year)


def _fmt_bytes(n: int) -> str:
    if n <= 0:
        return "0 B"
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if n < 1024:
            return f"{n:,.0f} {unit}"
        n /= 1024.0
    return f"{n:.1f} PB"


st.markdown(
    """
    <style>
      .hero {
        padding: 20px 24px; border-radius: 12px;
        background: radial-gradient(1200px 450px at 10% 0%, #172233 0%, #0E1117 60%);
        border: 1px solid rgba(255,255,255,0.06);
      }
      .hero h1 {margin: 0 0 6px 0; font-size: 1.6rem;}
      .hero p {margin: 0; opacity: 0.9}
    </style>
    <div class="hero">
      <h1>⚽ OpenFootball Analytics</h1>
      <p>Clean, structured football data with fast exploration.</p>
      <p style="opacity:0.6 ;font-size:0.9rem">Transfermarkt dataset (2012–2024): 60k+ games, 400+ clubs, 30k+ players, 400k+ valuations, 1.2M+ appearances.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.divider()

nav_cols = st.columns([1, 1, 1, 1, 1, 1, 1, 1, 1])
with nav_cols[0]:
    st.page_link("pages/1_Leagues.py", label="Leagues")
with nav_cols[1]:
    st.page_link("pages/2_Clubs.py", label="Clubs")
with nav_cols[2]:
    st.page_link("pages/3_Players.py", label="Players")
with nav_cols[3]:
    st.page_link("pages/4_Player_Leaderboards.py", label="Leaderboards")
with nav_cols[4]:
    st.page_link("pages/5_Formations.py", label="Formations")
with nav_cols[5]:
    st.page_link("pages/6_Managers.py", label="Managers")
with nav_cols[6]:
    st.page_link("pages/7_Transfers.py", label="Transfers")
with nav_cols[7]:
    st.page_link("pages/8_Market_Movers.py", label="Movers")
with nav_cols[8]:
    st.page_link("pages/9_Compare.py", label="Compare")

st.divider()

try:
    seasons_raw = api.get_seasons() or []
    competitions_raw = api.get_competitions() or []
except Exception:
    seasons_raw, competitions_raw = [], []

season_labels = _season_labels(seasons_raw)
latest_season = _latest_season_label(season_labels)
comp_list = get_list(competitions_raw, key="competitions") or get_list(competitions_raw)
comp_count = len(comp_list) if isinstance(comp_list, list) else 0

st.markdown("#### Quick Search")
cs = st.columns([4, 4, 4])
with cs[0]:
    with st.form("home_player_form"):
        q_player = st.text_input("Player", "", placeholder="Type player name…")
        submit_p = st.form_submit_button("Search")
    if submit_p and (q_player or "").strip():
        st.session_state["player_insights_search_seed_query"] = q_player.strip()
        try:
            st.switch_page("pages/3_Players.py")
        except Exception:
            st.page_link("pages/3_Players.py", label="Open Players")

with cs[1]:
    with st.form("home_club_form"):
        q_club = st.text_input("Club", "", placeholder="Type club name…")
        submit_c = st.form_submit_button("Search")
    if submit_c and (q_club or "").strip():
        st.session_state["club_dashboard_search_seed_query"] = q_club.strip()
        try:
            st.switch_page("pages/2_Clubs.py")
        except Exception:
            st.page_link("pages/2_Clubs.py", label="Open Clubs")
st.divider()

st.markdown("#### Highlights")
hl = st.columns(2)

with hl[0]:
    st.subheader("Top Contribution (Latest Season)")
    if latest_season:
        try:
            top = api.players_top(
                latest_season,
                metric="total_goals_and_assists",
                min_minutes=300,
                limit=25,
            )
        except Exception:
            top = []
        from pandas import DataFrame as _DF

        top_df = _DF(
            get_list(top)
            or get_list(top, key="players")
            or get_list(top, key="leaders")
            or []
        )
        if not top_df.empty:
            import pandas as _pd

            if "total_goals_and_assists" not in top_df.columns and {
                "goals",
                "assists",
            }.issubset(set(top_df.columns)):
                g = _pd.to_numeric(top_df["goals"], errors="coerce").fillna(0)
                a = _pd.to_numeric(top_df["assists"], errors="coerce").fillna(0)
                top_df["total_goals_and_assists"] = g + a
            sort_key = (
                "total_goals_and_assists"
                if "total_goals_and_assists" in top_df.columns
                else ("goals" if "goals" in top_df.columns else None)
            )
            if sort_key:
                top_df[sort_key] = _pd.to_numeric(
                    top_df[sort_key], errors="coerce"
                ).fillna(0)
                top_df = top_df.sort_values(
                    by=sort_key, ascending=False, kind="mergesort"
                )
        display_cols = [
            c
            for c in [
                "player_name",
                "club_name",
                "total_goals_and_assists",
                "goals",
                "assists",
            ]
            if c in top_df.columns
        ]
        if not top_df.empty and display_cols:
            st.dataframe(
                top_df[display_cols].head(10), use_container_width=True, hide_index=True
            )
        else:
            st.caption("No data available.")
    else:
        st.caption("Latest season is not available.")

with hl[1]:
    st.subheader("Most Expensive (Latest Season)")
    if latest_season:
        try:
            vp = api.value_perf(latest_season) or []
        except Exception:
            vp = []
        from pandas import DataFrame as _DF
        import pandas as _pd

        val_df = _DF(get_list(vp) or [])

        def _fmt_currency(v: Any) -> str:
            try:
                n = float(v)
                if abs(n) >= 1_000_000:
                    return f"€{n/1_000_000:.1f}M"
                if abs(n) >= 1_000:
                    return f"€{n/1_000:.0f}K"
                return f"€{n:,.0f}"
            except Exception:
                return str(v)

        value_col = None
        for c in ["last_market_value", "max_market_value", "market_value", "value"]:
            if c in val_df.columns:
                value_col = c
                break
        if value_col:
            val_df[value_col] = _pd.to_numeric(
                val_df[value_col], errors="coerce"
            ).fillna(0)
            val_df = val_df.sort_values(by=value_col, ascending=False)
            cols = [
                c
                for c in ["player_name", "club_name", value_col]
                if c in val_df.columns
            ]
            try:
                fmt = {value_col: _fmt_currency}
                st.dataframe(
                    val_df[cols].head(10).style.format(fmt),
                    use_container_width=True,
                    hide_index=True,
                )
            except Exception:
                df2 = val_df[cols].head(10).copy()
                df2[value_col] = df2[value_col].apply(_fmt_currency)
                st.dataframe(df2, use_container_width=True, hide_index=True)
        else:
            st.caption("No valuation data.")
    else:
        st.caption("Latest season is not available.")

st.divider()

st.markdown("#### Leaderboards (Latest Season)")
lb_cols = st.columns([4, 2, 6])
with lb_cols[0]:
    lb_metric = st.selectbox(
        "Metric",
        [
            "total_goals_and_assists",
            "goals",
            "assists",
            "goals_per90",
            "assists_per90",
            "goal_plus_assist_per90",
            "efficiency_score",
            "minutes_played",
        ],
        index=0,
        key="home_lb_metric",
    )
with lb_cols[1]:
    lb_min = st.slider("Min minutes", 0, 3000, 600, 30, key="home_lb_min")

if latest_season:
    try:
        lb = api.players_top(
            latest_season, metric=lb_metric, min_minutes=lb_min, limit=50
        )
    except Exception:
        lb = []
    from pandas import DataFrame as _DF
    import pandas as _pd

    lb_df = _DF(
        get_list(lb) or get_list(lb, key="players") or get_list(lb, key="leaders") or []
    )
    # Derive where needed
    if (
        lb_metric == "total_goals_and_assists"
        and not lb_df.empty
        and lb_metric not in lb_df.columns
    ):
        if {"goals", "assists"}.issubset(lb_df.columns):
            g = _pd.to_numeric(lb_df["goals"], errors="coerce").fillna(0)
            a = _pd.to_numeric(lb_df["assists"], errors="coerce").fillna(0)
            lb_df[lb_metric] = g + a
    if lb_metric in lb_df.columns:
        lb_df[lb_metric] = _pd.to_numeric(lb_df[lb_metric], errors="coerce")
        lb_df = lb_df.sort_values(by=lb_metric, ascending=False, kind="mergesort")
    if lb_df.empty:
        st.caption("No leaderboard data for latest season.")
    else:
        display_cols = [
            c for c in ["player_name", "club_name", lb_metric] if c in lb_df.columns
        ]
        st.dataframe(lb_df[display_cols], use_container_width=True, hide_index=True)
else:
    st.caption("Latest season is not available.")
