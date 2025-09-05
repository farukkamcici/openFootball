import os
import sys
from typing import List, Dict, Any

import streamlit as st

_CUR_DIR = os.path.dirname(__file__)
_APP_ROOT = os.path.dirname(_CUR_DIR)
if _APP_ROOT not in sys.path:
    sys.path.insert(0, _APP_ROOT)

try:
    from app import api_client as api
    from app.charts import COLOR_GAIN, COLOR_LOSS
    from app.utils import (
        inject_theme,
        filter_bar,
        empty_state,
        search_select,
        df_from_list,
        render_sidebar,
    )
except ModuleNotFoundError:
    import api_client as api
    from charts import COLOR_GAIN, COLOR_LOSS
    from utils import (
        inject_theme,
        filter_bar,
        empty_state,
        search_select,
        df_from_list,
        render_sidebar,
    )


inject_theme()
render_sidebar()
st.title("Compare")

tabs = st.tabs(["Players", "Clubs"])


def _coerce_float(v: Any) -> float:
    try:
        if v is None:
            return 0.0
        if isinstance(v, (int, float)):
            return float(v)
        return float(str(v).replace(",", "."))
    except Exception:
        return 0.0


with tabs[0]:
    st.subheader("Player Compare")
    season, competition = filter_bar(
        include_season=True, include_competition=True, key_prefix="cmp_players"
    )
    col_a, col_b = st.columns(2)
    with col_a:
        p1, pmap1 = search_select(
            label="Player A",
            search_fn=api.search_players,
            result_keys=("players", "results"),
            id_keys=("id", "player_id"),
            name_keys=("name", "player_name"),
            key="cmp_player_a",
        )
    with col_b:
        p2, pmap2 = search_select(
            label="Player B",
            search_fn=api.search_players,
            result_keys=("players", "results"),
            id_keys=("id", "player_id"),
            name_keys=("name", "player_name"),
            key="cmp_player_b",
        )
    selected_players: List[str] = [pid for pid in [p1, p2] if pid]
    if not season or len(selected_players) < 2:
        empty_state("Pick a season and at least two players (competition optional).")
    else:
        # Fetch stats per player (competition-specific if provided, else overall season)
        records: List[Dict[str, Any]] = []
        for pid in selected_players:
            if competition:
                data = api.player_season_competition(pid, season, competition)
            else:
                data = api.player_season(pid, season)
            if isinstance(data, dict):
                records.append(data)
        rows = df_from_list(records)

        if rows.empty:
            empty_state("No comparable player stats found for selection.")
        else:
            # Only Key Stats panel
            pass

            # Under-radar stat panel: left player vs right player with metric in middle
            if len(rows) >= 2:
                # Centered symmetric Key Stats with color highlighting
                pleft = rows.iloc[0]
                pright = rows.iloc[1]
                st.markdown("---")
                st.subheader("Key Stats")

                def _fmt_int(x):
                    try:
                        return int(float(x))
                    except Exception:
                        return None

                def _fmt_float(x, d=2):
                    try:
                        return round(float(x), d)
                    except Exception:
                        return None

                def _fmt_currency(x):
                    try:
                        return f"€{int(float(x)):,}"
                    except Exception:
                        return None

                def _styled(vl, vr, invert: bool = False):
                    lv = None if vl is None else float(vl)
                    rv = None if vr is None else float(vr)
                    if lv is None or rv is None:
                        return (
                            vl if vl is not None else "-",
                            vr if vr is not None else "-",
                            "",
                            "",
                        )
                    if lv == rv:
                        return (vl, vr, "", "")
                    left_better = (lv > rv) if not invert else (lv < rv)
                    return (
                        vl,
                        vr,
                        f"color:{COLOR_GAIN}" if left_better else f"color:{COLOR_LOSS}",
                        f"color:{COLOR_GAIN}"
                        if not left_better
                        else f"color:{COLOR_LOSS}",
                    )

                metrics = [
                    (
                        "Minutes",
                        pleft.get("minutes_played"),
                        pright.get("minutes_played"),
                        False,
                    ),
                    (
                        "Games",
                        pleft.get("games_played"),
                        pright.get("games_played"),
                        False,
                    ),
                    ("Goals", pleft.get("goals"), pright.get("goals"), False),
                    ("Assists", pleft.get("assists"), pright.get("assists"), False),
                    (
                        "G+A/90",
                        pleft.get("goal_plus_assist_per90"),
                        pright.get("goal_plus_assist_per90"),
                        False,
                    ),
                    (
                        "Goals/90",
                        pleft.get("goals_per90"),
                        pright.get("goals_per90"),
                        False,
                    ),
                    (
                        "Assists/90",
                        pleft.get("assists_per90"),
                        pright.get("assists_per90"),
                        False,
                    ),
                    (
                        "Efficiency",
                        pleft.get("efficiency_score"),
                        pright.get("efficiency_score"),
                        False,
                    ),
                    (
                        "Season Value (€)",
                        pleft.get("season_last_value_eur"),
                        pright.get("season_last_value_eur"),
                        False,
                    ),
                    (
                        "Yellow Cards",
                        pleft.get("yellow_cards"),
                        pright.get("yellow_cards"),
                        True,
                    ),
                    (
                        "Red Cards",
                        pleft.get("red_cards"),
                        pright.get("red_cards"),
                        True,
                    ),
                ]

                outer = st.columns([1, 2, 1])
                with outer[1]:

                    def _format_by_label(label: str, val):
                        if val is None or val == "-":
                            return "-"
                        if label.endswith("(€)"):
                            return _fmt_currency(val) or "-"
                        if "/90" in label or label in ("Efficiency",):
                            return f"{_fmt_float(val) if _fmt_float(val) is not None else 0:.2f}"
                        # integers by default
                        vi = _fmt_int(val)
                        return f"{vi:,}" if vi is not None else "-"

                    for label, lv, rv, invert in metrics:
                        lv_v, rv_v, lc, rc = _styled(lv, rv, invert=invert)
                        cL, cM, cR = st.columns([4, 2, 4])
                        with cL:
                            st.markdown(
                                f"<div style='text-align:right; {lc}'><strong>{_format_by_label(label, lv_v)}</strong></div>",
                                unsafe_allow_html=True,
                            )
                        with cM:
                            st.caption(label)
                        with cR:
                            st.markdown(
                                f"<div style='{rc}'><strong>{_format_by_label(label, rv_v)}</strong></div>",
                                unsafe_allow_html=True,
                            )


with tabs[1]:
    st.subheader("Club Compare")
    season, competition = filter_bar(
        include_season=True, include_competition=True, key_prefix="cmp_clubs"
    )
    all_time = st.checkbox(
        "All time (aggregate across seasons)", key="cmp_clubs_all_time"
    )
    col_a, col_b = st.columns(2)
    with col_a:
        c1, cmap1 = search_select(
            label="Club A",
            search_fn=api.search_clubs,
            result_keys=("clubs", "results"),
            id_keys=("id", "club_id"),
            name_keys=("name", "club_name"),
            key="cmp_club_a",
        )
    with col_b:
        c2, cmap2 = search_select(
            label="Club B",
            search_fn=api.search_clubs,
            result_keys=("clubs", "results"),
            id_keys=("id", "club_id"),
            name_keys=("name", "club_name"),
            key="cmp_club_b",
        )
    selected_clubs: List[str] = [cid for cid in [c1, c2] if cid]
    if (not season and not all_time) or len(selected_clubs) < 2:
        empty_state("Pick a season (or All time) and two clubs.")
    else:
        import pandas as _pd

        def _seasons_list() -> List[str]:
            try:
                data = api.get_seasons() or []
                if isinstance(data, list):
                    return [
                        str(it.get("season"))
                        for it in data
                        if isinstance(it, dict) and it.get("season") is not None
                    ]
            except Exception:
                pass
            return []

        if all_time:
            seasons_to_use = _seasons_list()
        else:
            seasons_to_use = [season]

        # Aggregate metrics per selected club
        agg = {
            cid: {
                "games_played": 0.0,
                "points": 0.0,
                "goals_for": 0.0,
                "goals_against": 0.0,
                "goal_difference": 0.0,
            }
            for cid in selected_clubs
        }

        if competition:
            # Use league-split to scope to competition
            for cid in selected_clubs:
                for s in seasons_to_use:
                    split = api.club_league_split(cid, s) or []
                    for r in split or []:
                        if (
                            isinstance(r, dict)
                            and r.get("competition_id") == competition
                        ):
                            agg[cid]["games_played"] += float(
                                r.get("games_played", 0) or 0
                            )
                            agg[cid]["points"] += float(r.get("points", 0) or 0)
                            agg[cid]["goals_for"] += float(r.get("goals_for", 0) or 0)
                            agg[cid]["goals_against"] += float(
                                r.get("goals_against", 0) or 0
                            )
                            agg[cid]["goal_difference"] += float(
                                r.get("goal_difference", 0) or 0
                            )
        else:
            # Use compare_clubs and sum across competitions
            for s in seasons_to_use:
                ids_str = ",".join(selected_clubs)
                res = api.compare_clubs(ids_str, s) or []
                df = df_from_list(res)
                if not isinstance(df, _pd.DataFrame) or df.empty:
                    continue
                for col in [
                    "games_played",
                    "points",
                    "goals_for",
                    "goals_against",
                    "goal_difference",
                ]:
                    df[col] = _pd.to_numeric(df.get(col), errors="coerce").fillna(0)
                grouped = df.groupby("club_id")[
                    [
                        "games_played",
                        "points",
                        "goals_for",
                        "goals_against",
                        "goal_difference",
                    ]
                ].sum()
                for cid, row in grouped.iterrows():
                    cid_str = str(int(cid))
                    if cid_str in agg:
                        for k in agg[cid_str]:
                            agg[cid_str][k] += float(row.get(k, 0) or 0)

        # Build Key Stats view
        if len(selected_clubs) >= 2:
            left = agg[selected_clubs[0]]
            right = agg[selected_clubs[1]]
            st.markdown("---")
            st.subheader("Key Stats")

            def _style_vals(lv, rv, invert=False):
                try:
                    lvf = float(lv)
                    rvf = float(rv)
                except Exception:
                    return (lv, rv, "", "")
                if lvf == rvf:
                    return (lv, rv, "", "")
                left_better = (lvf > rvf) if not invert else (lvf < rvf)
                lc = f"color:{COLOR_GAIN}" if left_better else f"color:{COLOR_LOSS}"
                rc = f"color:{COLOR_GAIN}" if not left_better else f"color:{COLOR_LOSS}"
                return (lv, rv, lc, rc)

            def _ppg(total_points, total_games) -> float:
                try:
                    gp = float(total_games)
                    return round(float(total_points) / gp, 2) if gp > 0 else 0.0
                except Exception:
                    return 0.0

            metrics = [
                ("Points", left["points"], right["points"], False),
                (
                    "PPG",
                    _ppg(left["points"], left["games_played"]),
                    _ppg(right["points"], right["games_played"]),
                    False,
                ),
                ("Games", left["games_played"], right["games_played"], False),
                ("Goals For", left["goals_for"], right["goals_for"], False),
                ("Goals Against", left["goals_against"], right["goals_against"], True),
                ("Goal Diff", left["goal_difference"], right["goal_difference"], False),
            ]
            outer2 = st.columns([1, 2, 1])
            with outer2[1]:

                def _fmt_club_val(label: str, v):
                    try:
                        vf = float(v)
                    except Exception:
                        return v
                    if label == "PPG":
                        return f"{vf:.2f}"
                    try:
                        return f"{int(vf)}"
                    except Exception:
                        return f"{vf}"

                for label, lv, rv, inv in metrics:
                    lv_v, rv_v, lc, rc = _style_vals(lv, rv, invert=inv)
                    cL, cM, cR = st.columns([4, 2, 4])
                    with cL:
                        st.markdown(
                            f"<div style='text-align:right; {lc}'><strong>{_fmt_club_val(label, lv_v)}</strong></div>",
                            unsafe_allow_html=True,
                        )
                    with cM:
                        st.caption(label)
                    with cR:
                        st.markdown(
                            f"<div style='{rc}'><strong>{_fmt_club_val(label, rv_v)}</strong></div>",
                            unsafe_allow_html=True,
                        )
