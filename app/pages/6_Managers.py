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
        kpi_grid,
        get_list,
        search_select,
        inject_theme,
        section_tabs,
    )
except ModuleNotFoundError:
    import api_client as api
    from utils import (
        df_from_list,
        empty_state,
        kpi_grid,
        get_list,
        search_select,
        inject_theme,
        section_tabs,
    )


inject_theme()
st.title("Managers")

sel_manager, _ = search_select(
    label="Manager",
    search_fn=api.search_managers,
    result_keys=("managers", "results"),
    id_keys=("name", "manager_name", "id"),
    name_keys=("name", "manager_name"),
    key="managers_search",
    min_chars=1,
)
perf = api.managers_performance()
best_forms = api.managers_best_formations() or {}

tab_detail, tab_leaderboard, tab_best = section_tabs(
    ["Manager Detail", "Leaderboard", "Best Formations"], key="managers_tabs"
)

with tab_detail:
    # Selected manager details (shown only when a manager is selected)
    if sel_manager:
        try:
            cand = api.search_managers(sel_manager) or []
        except Exception:
            cand = []
        if isinstance(cand, list) and cand:
            row = next(
                (
                    c
                    for c in cand
                    if str(c.get("manager_name", "")).lower()
                    == str(sel_manager).lower()
                ),
                cand[0],
            )
            gp = row.get("games_played") or 0
            ppg = row.get("ppg") or 0
            wr = row.get("win_rate") or 0
            kpi_grid(
                [
                    ("Games", f"{gp}"),
                    (
                        "PPG",
                        f"{ppg:.2f}" if isinstance(ppg, (int, float)) else str(ppg),
                    ),
                    (
                        "Win %",
                        f"{wr:.1f}%" if isinstance(wr, (int, float)) else str(wr),
                    ),
                ]
            )

        st.subheader(f"{sel_manager} Preferred Formation")
        form = api.managers_formation(sel_manager) or {}
        pref_df = df_from_list(get_list(form, key="formations"))
        if pref_df.empty:
            empty_state("No specific formation data for manager.")
        else:
            st.dataframe(pref_df, use_container_width=True, hide_index=True)
    else:
        empty_state("Search and select a manager.")

with tab_leaderboard:
    st.subheader("Manager Leaderboard")
    perf_df = df_from_list(get_list(perf, key="managers"))
    if perf_df.empty:
        empty_state("No manager performance data.")
    else:
        st.dataframe(perf_df, use_container_width=True, hide_index=True)

with tab_best:
    st.subheader("Best Performing Formations")
    best_df = df_from_list(get_list(best_forms, key="formations"))
    if best_df.empty:
        empty_state("No formation highlights.")
    else:
        st.dataframe(best_df, use_container_width=True, hide_index=True)
