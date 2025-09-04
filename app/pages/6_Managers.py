import streamlit as st

import api_client as api
from utils import df_from_list, empty_state, kpi_grid, get_list, search_select


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

# Selected manager details (shown only when a manager is selected)
if sel_manager:
    # Quick summary from search endpoint
    try:
        cand = api.search_managers(sel_manager) or []
    except Exception:
        cand = []
    if isinstance(cand, list) and cand:
        # pick exact match if exists, else first
        row = next(
            (
                c
                for c in cand
                if str(c.get("manager_name", "")).lower() == str(sel_manager).lower()
            ),
            cand[0],
        )
        gp = row.get("games_played") or 0
        ppg = row.get("ppg") or 0
        wr = row.get("win_rate") or 0
        kpi_grid(
            [
                ("Games", f"{gp}"),
                ("PPG", f"{ppg:.2f}" if isinstance(ppg, (int, float)) else str(ppg)),
                ("Win %", f"{wr:.1f}%" if isinstance(wr, (int, float)) else str(wr)),
            ]
        )

    st.subheader(f"{sel_manager} Preferred Formation")
    form = api.managers_formation(sel_manager) or {}
    pref_df = df_from_list(get_list(form, key="formations"))
    if pref_df.empty:
        empty_state("No specific formation data for manager.")
    else:
        st.dataframe(pref_df, use_container_width=True, hide_index=True)

st.subheader("Manager Leaderboard")
perf_df = df_from_list(get_list(perf, key="managers"))
if perf_df.empty:
    empty_state("No manager performance data.")
else:
    st.dataframe(perf_df, use_container_width=True, hide_index=True)

st.subheader("Best Performing Formations")
best_df = df_from_list(get_list(best_forms, key="formations"))
if best_df.empty:
    empty_state("No formation highlights.")
else:
    st.dataframe(best_df, use_container_width=True, hide_index=True)
