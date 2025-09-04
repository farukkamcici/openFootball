from __future__ import annotations

from typing import Iterable, List, Optional, Tuple, Any, Sequence, Dict, Callable

import pandas as pd
import streamlit as st

import api_client as api


def empty_state(message: str = "No data available.") -> None:
    # Minimal, non-intrusive notice
    st.caption(message)


def kpi_grid(items: Iterable[Tuple[str, str]]) -> None:
    items = list(items)
    cols = st.columns(len(items))
    for col, (label, value) in zip(cols, items):
        with col:
            st.metric(label, value)


def _as_list(obj: Any, key: Optional[str] = None) -> List[Any]:
    if isinstance(obj, dict):
        value = obj.get(key) if key else None
        if isinstance(value, list):
            return value
        # If dict but no key or not list, return empty
        return []
    if isinstance(obj, list):
        return obj
    return []


def get_list(obj: Any, key: Optional[str] = None) -> List[Any]:
    """Public helper to safely extract a list from dict/list/None."""
    return _as_list(obj, key)


def _extract_first(d: Dict[str, Any], candidates: Sequence[str]) -> Optional[str]:
    for k in candidates:
        if k in d and d[k] is not None:
            return str(d[k])
    return None


def _season_options(obj: Any) -> List[str]:
    items = _as_list(obj, key="seasons")
    out: List[str] = []
    for it in items:
        if isinstance(it, dict):
            label = _extract_first(
                it, ("season", "year", "name", "label", "code", "id")
            )
            if label:
                out.append(label)
        else:
            out.append(str(it))
    return out


def _competition_options(obj: Any) -> List[Tuple[str, str]]:
    items = _as_list(obj, key="competitions")
    out: List[Tuple[str, str]] = []
    for it in items:
        if isinstance(it, dict):
            label = _extract_first(
                it, ("name", "competition_name", "label", "code", "id")
            )
            value = _extract_first(it, ("id", "competition_id", "code", "name"))
            if label and value:
                out.append((label, value))
        else:
            s = str(it)
            out.append((s, s))
    return out


def _cached_meta_lists() -> Tuple[List[str], List[Tuple[str, str]]]:
    """Fetch seasons and competitions once per session with robust fallbacks."""
    try:
        seasons = st.session_state.get("_meta_seasons_cache")
        if seasons is None:
            seasons = api.get_seasons() or []
            st.session_state["_meta_seasons_cache"] = seasons
    except Exception:
        seasons = []

    try:
        competitions = st.session_state.get("_meta_competitions_cache")
        if competitions is None:
            competitions = api.get_competitions() or []
            st.session_state["_meta_competitions_cache"] = competitions
    except Exception:
        competitions = []

    season_list: List[str] = _season_options(seasons)
    comp_pairs: List[Tuple[str, str]] = _competition_options(competitions)
    return season_list, comp_pairs


def sidebar_filters() -> Tuple[Optional[str], Optional[str]]:
    with st.sidebar:
        st.markdown("### Filters")
        season_list, comp_pairs = _cached_meta_lists()

        # Prepend a "no filter" option so filters are optional
        season_options = ["-"] + season_list
        comp_options: List[Tuple[str, str]] = [("-", "-")] + comp_pairs

        season_choice = st.selectbox("Season", season_options, index=0)
        comp_choice = st.selectbox(
            "Competition",
            comp_options,
            index=0,
            format_func=lambda pair: pair[0] if isinstance(pair, tuple) else str(pair),
        )

    season = None if season_choice == "-" else season_choice
    competition = (
        None
        if (isinstance(comp_choice, tuple) and comp_choice[1] == "-")
        else (comp_choice[1] if isinstance(comp_choice, tuple) else str(comp_choice))
    )
    return season, competition


def inject_theme() -> None:
    """Inject minimal CSS tweaks for cleaner spacing and readability.

    Keeps visuals subtle and consistent across pages.
    """
    st.markdown(
        """
        <style>
        /* Tighten default padding slightly */
        .block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
        /* Dataframe header emphasis */
        thead tr th {font-weight: 600 !important;}
        /* Metric labels a bit calmer */
        [data-testid="stMetricLabel"] div {opacity: 0.8;}
        /* Plotly container breathing room */
        .element-container .plotly {padding: 0.25rem 0.25rem;}
        /* Form submit buttons spacing */
        form [type="submit"] {margin-top: 0.25rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def section_tabs(labels: Sequence[str], key: str):
    """Render tabs and return tab context managers list.

    Wrapper to keep a single place to adjust behavior later if needed.
    """
    return st.tabs(labels)


def filter_bar(
    include_season: bool = True,
    include_competition: bool = False,
    key_prefix: str = "filters",
) -> Tuple[Optional[str], Optional[str]]:
    """Render a horizontal filter bar inside the page.

    Returns (season, competition_id) where either can be None if not included/selected.
    """
    season_list, comp_pairs = _cached_meta_lists()

    season_choice: Optional[str] = None
    comp_choice: Optional[Tuple[str, str]] = None

    # Build columns layout based on included controls
    if include_season and include_competition:
        cols = st.columns([3, 3, 6])
        with cols[0]:
            season_choice = st.selectbox(
                "Season",
                ["-"] + season_list,
                index=0,
                key=f"{key_prefix}_season",
            )
        with cols[1]:
            comp_choice = st.selectbox(
                "Competition",
                [("-", "-")] + comp_pairs,
                index=0,
                format_func=lambda pair: pair[0]
                if isinstance(pair, tuple)
                else str(pair),
                key=f"{key_prefix}_competition",
            )
    elif include_season:
        cols = st.columns([4, 8])
        with cols[0]:
            season_choice = st.selectbox(
                "Season",
                ["-"] + season_list,
                index=0,
                key=f"{key_prefix}_season",
            )
    elif include_competition:
        cols = st.columns([4, 8])
        with cols[0]:
            comp_choice = st.selectbox(
                "Competition",
                [("-", "-")] + comp_pairs,
                index=0,
                format_func=lambda pair: pair[0]
                if isinstance(pair, tuple)
                else str(pair),
                key=f"{key_prefix}_competition",
            )
    else:
        # No filters requested
        return None, None

    season = None if (season_choice in (None, "-")) else str(season_choice)
    competition = None
    if comp_choice is not None:
        competition = (
            None
            if (isinstance(comp_choice, tuple) and comp_choice[1] == "-")
            else (
                comp_choice[1] if isinstance(comp_choice, tuple) else str(comp_choice)
            )
        )
    return season, competition


def df_from_list(items: Optional[List[dict]]) -> pd.DataFrame:
    return pd.DataFrame(items or [])


def _first_nonempty(d: Dict[str, Any], keys: Sequence[str]) -> Optional[str]:
    for k in keys:
        if k in d and d[k] not in (None, ""):
            return str(d[k])
    return None


def search_select(
    label: str,
    search_fn: Callable[[str], Any],
    result_keys: Sequence[str],
    id_keys: Sequence[str],
    name_keys: Sequence[str],
    key: Optional[str] = None,
    min_chars: int = 2,
) -> Tuple[Optional[str], Dict[str, str]]:
    """Render a search box + select results workflow that submits on Enter.

    Returns (selected_id, id->label map).
    """
    form_key = key or f"{label.lower().replace(' ', '_')}_search_form"
    q_key = f"{form_key}_q"
    opts_key = f"{form_key}_options"
    sel_key = f"{form_key}_selected"
    with st.form(form_key):
        q = st.text_input(
            f"Search {label}", "", placeholder=f"Type {label} name...", key=q_key
        )
        submitted = st.form_submit_button("Search")

    selected_id: Optional[str] = None
    id_to_label: Dict[str, str] = {}

    if not submitted:
        # If we have previous options in session, render the selectbox to allow changing selection
        prev_options: Dict[str, str] = st.session_state.get(opts_key, {})
        prev_selected: Optional[str] = st.session_state.get(sel_key)
        if prev_options:
            ids = list(prev_options.keys())
            # Keep currently selected if still present
            index = ids.index(prev_selected) if prev_selected in ids else 0
            selected_id = st.selectbox(
                label, ids, index=index, format_func=lambda k: prev_options.get(k, k)
            )
            st.session_state[sel_key] = selected_id
            return selected_id, prev_options
        return None, {}

    q = (q or "").strip()
    if len(q) < min_chars:
        empty_state(f"Type at least {min_chars} characters to search.")
        return None, {}

    try:
        res = search_fn(q) or {}
    except Exception:
        res = {}

    items = get_list(res)
    if not items:
        for rk in result_keys:
            items = get_list(res, key=rk)
            if items:
                break

    for it in items:
        if not isinstance(it, dict):
            continue
        rid = _first_nonempty(it, id_keys)
        rname = _first_nonempty(it, name_keys)
        if rid and rname:
            id_to_label[str(rid)] = str(rname)

    ids = list(id_to_label.keys())
    if not ids:
        empty_state(f"No {label.lower()} found for '{q}'.")
        return None, {}

    # Persist options and selection across reruns
    st.session_state[opts_key] = id_to_label
    prev_selected: Optional[str] = st.session_state.get(sel_key)
    index = ids.index(prev_selected) if prev_selected in ids else 0
    selected_id = st.selectbox(
        label, ids, index=index, format_func=lambda k: id_to_label.get(k, k)
    )
    st.session_state[sel_key] = selected_id
    return selected_id, id_to_label
