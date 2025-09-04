import streamlit as st

import api_client as api
from utils import df_from_list, empty_state, get_list, search_select, filter_bar
from charts import top_spenders_bar, free_vs_paid_chart, fee_timeline


st.title("Transfers")

# Player transfers
st.subheader("Player Transfer History")
player_id, _ = search_select(
    label="Player",
    search_fn=api.search_players,
    result_keys=("players", "results"),
    id_keys=("id", "player_id"),
    name_keys=("name", "player_name"),
    key="transfers_player_search",
)


def _fmt_currency(v):
    try:
        n = float(v)
        if abs(n) >= 1_000_000:
            return f"€{n/1_000_000:.1f}M"
        if abs(n) >= 1_000:
            return f"€{n/1_000:.0f}K"
        return f"€{n:,.0f}"
    except Exception:
        return v


def _tag_style_for_direction(v: str) -> str:
    try:
        s = str(v).strip().lower()
    except Exception:
        s = ""
    if s == "in":
        return "background-color:#1b5e20;color:white;font-weight:600;border-radius:4px;padding:0 6px;"
    if s == "out":
        return "background-color:#b71c1c;color:white;font-weight:600;border-radius:4px;padding:0 6px;"
    return ""


def _tag_style_for_category(v: str) -> str:
    try:
        s = str(v).strip().lower()
    except Exception:
        s = ""
    if "loan return" in s:
        return "background-color:#546e7a;color:white;border-radius:4px;padding:0 6px;"
    if "loan" in s:
        return "background-color:#1976d2;color:white;border-radius:4px;padding:0 6px;"
    if "free" in s:
        return "background-color:#2e7d32;color:white;border-radius:4px;padding:0 6px;"
    if s:
        return "background-color:#37474f;color:white;border-radius:4px;padding:0 6px;"
    return ""


if player_id:
    ptx = api.transfers_player(player_id) or []
    ptx_df = df_from_list(get_list(ptx) or get_list(ptx, key="transfers"))
    if ptx_df.empty:
        empty_state("No transfers for player.")
    else:
        # Minimal, meaningful columns for end users
        disp_cols = [
            c
            for c in [
                "transfer_date",
                "from_club_name",
                "to_club_name",
                "transfer_category",
                "transfer_fee",
            ]
            if c in ptx_df.columns
        ]
        show_df = ptx_df[disp_cols].copy()
        if "transfer_fee" in show_df.columns:
            show_df["transfer_fee"] = show_df["transfer_fee"].apply(_fmt_currency)
        # Style: currency + category tag
        try:
            styler = show_df.style.format({"transfer_fee": _fmt_currency})
            if "transfer_category" in show_df.columns:
                styler = styler.applymap(
                    _tag_style_for_category, subset=["transfer_category"]
                )
            st.dataframe(styler, use_container_width=True, hide_index=True)
        except Exception:
            st.dataframe(show_df, use_container_width=True, hide_index=True)

        # Beautified fee timeline if fees exist
        if {"transfer_date", "transfer_fee"}.issubset(ptx_df.columns):
            fee_df = (
                ptx_df[["transfer_date", "transfer_fee"]]
                .copy()
                .sort_values(by="transfer_date")
            )
            st.plotly_chart(fee_timeline(fee_df), use_container_width=True)
else:
    empty_state("Search a player and press Enter.")

# Club transfers (requires a season for the summary)
st.subheader("Club Transfers Summary")
club_id, _ = search_select(
    label="Club",
    search_fn=lambda q: api.search_clubs(q),
    result_keys=("clubs", "results"),
    id_keys=("id", "club_id"),
    name_keys=("name", "club_name"),
    key="transfers_club_search",
)


def _to_long_season(s: str) -> str:
    try:
        if "/" in str(s):
            return str(s)
        y = int(str(s)[:4])
        return f"{y}/{y+1}"
    except Exception:
        return str(s)


if club_id:
    # Local season picker for this section
    seasons = api.get_seasons() or []
    season_opts = ["-"] + [str(it.get("season", it)) for it in (seasons or [])]
    sel_season = st.selectbox(
        "Season", season_opts, index=0, key="transfers_club_season"
    )
    if sel_season and sel_season != "-":
        api_season = _to_long_season(sel_season)
        ctx = api.transfers_club(club_id, api_season) or {}
        # Response is a single object; put into a list for DataFrame
        ctx_df = df_from_list(
            [ctx] if isinstance(ctx, dict) else get_list(ctx, key="summary")
        )
        if ctx_df.empty:
            empty_state("No club transfer summary.")
        else:
            # Show only key columns
            keep = [
                c
                for c in [
                    "club_name",
                    "incoming_total",
                    "outgoing_total",
                    "transfer_spend",
                    "transfer_income",
                    "net_spend",
                ]
                if c in ctx_df.columns
            ]
            disp = ctx_df[keep].copy()
            try:
                fmt_map = {
                    c: _fmt_currency
                    for c in ["transfer_spend", "transfer_income", "net_spend"]
                    if c in disp.columns
                }
                styler = disp.style.format(fmt_map)
                st.dataframe(styler, use_container_width=True, hide_index=True)
            except Exception:
                for c in ["transfer_spend", "transfer_income", "net_spend"]:
                    if c in disp.columns:
                        disp[c] = disp[c].apply(_fmt_currency)
                st.dataframe(disp, use_container_width=True, hide_index=True)

        # Club transfer history: list incoming and outgoing players for the season
        lists = api.transfers_club_players(club_id, api_season) or {}
        inc_df = df_from_list(get_list(lists, key="incoming"))
        out_df = df_from_list(get_list(lists, key="outgoing"))
        if inc_df.empty and out_df.empty:
            empty_state("No transfer history for club in this season.")
        else:
            # Add direction and combine, keep meaningful columns
            if not inc_df.empty:
                inc_df = inc_df.assign(direction="In")
            if not out_df.empty:
                out_df = out_df.assign(direction="Out")
            try:
                import pandas as _pd

                hist_df = _pd.concat(
                    [df for df in [inc_df, out_df] if not df.empty], ignore_index=True
                )
            except Exception:
                hist_df = inc_df if not inc_df.empty else out_df
            # Sort by transfer_date desc when available
            try:
                hist_df = hist_df.sort_values(by="transfer_date", ascending=False)
            except Exception:
                pass
            # Select end-user columns
            cols = [
                c
                for c in [
                    "transfer_date",
                    "direction",
                    "player_name",
                    "from_club_name",
                    "to_club_name",
                    "transfer_category",
                    "transfer_fee",
                ]
                if c in hist_df.columns
            ]
            hist_df = hist_df[cols].copy()
            if "transfer_fee" in hist_df.columns:
                hist_df["transfer_fee"] = hist_df["transfer_fee"].apply(_fmt_currency)
            st.subheader("Club Transfer History")
            # Style: currency + colored tags for direction/category
            try:
                styler = hist_df.style
                if "transfer_fee" in hist_df.columns:
                    styler = styler.format({"transfer_fee": _fmt_currency})
                if "direction" in hist_df.columns:
                    styler = styler.applymap(
                        _tag_style_for_direction, subset=["direction"]
                    )
                if "transfer_category" in hist_df.columns:
                    styler = styler.applymap(
                        _tag_style_for_category, subset=["transfer_category"]
                    )
                st.dataframe(styler, use_container_width=True, hide_index=True)
            except Exception:
                st.dataframe(hist_df, use_container_width=True, hide_index=True)
    else:
        empty_state("Select a season for club summary.")
else:
    empty_state("Search a club and press Enter.")


def _drop_id_cols(df):
    cols = list(df.columns)
    drop_exact = {
        "id",
        "player_id",
        "club_id",
        "from_club_id",
        "to_club_id",
        "competition_id",
    }
    keep = [c for c in cols if not (c in drop_exact or c.endswith("_id"))]
    return df[keep] if keep else df


st.subheader("Transfers Overview")
# Shared filters for Top Spenders and Free vs Paid
ov_season, ov_competition = filter_bar(
    include_season=True, include_competition=True, key_prefix="transfers_overview"
)

st.markdown("### Top Spenders")
if ov_season and ov_competition:
    api_season_ts = _to_long_season(ov_season)
    spenders = api.transfers_top_spenders(api_season_ts, ov_competition) or []
    spenders_df = df_from_list(get_list(spenders) or get_list(spenders, key="spenders"))
    if spenders_df.empty:
        empty_state("No spenders data.")
    else:
        # Prefer chart + table
        st.plotly_chart(top_spenders_bar(spenders_df), use_container_width=True)
        # Minimal columns + euro formatting
        show_cols = [
            c
            for c in ["club_name", "transfer_spend", "transfer_income", "net_spend"]
            if c in spenders_df.columns
        ]
        spenders_df = (
            spenders_df[show_cols] if show_cols else _drop_id_cols(spenders_df)
        )
        # Style currency columns if present
        try:
            fmt_map = {
                c: _fmt_currency
                for c in ["transfer_spend", "transfer_income", "net_spend"]
                if c in spenders_df.columns
            }
            st.dataframe(
                spenders_df.style.format(fmt_map),
                use_container_width=True,
                hide_index=True,
            )
        except Exception:
            st.dataframe(spenders_df, use_container_width=True, hide_index=True)
else:
    empty_state("Select season and competition for top spenders.")

st.markdown("### Free vs Paid Distribution")
if ov_season and ov_competition:
    api_season_fp = _to_long_season(ov_season)
    free_paid = api.transfers_free_vs_paid(api_season_fp, ov_competition) or {}
    # Build chart-friendly output
    if isinstance(free_paid, dict):
        inc_free = int(free_paid.get("inc_free", 0) or 0)
        inc_paid = int(free_paid.get("inc_paid", 0) or 0)
        out_free = int(free_paid.get("out_free", 0) or 0)
        out_paid = int(free_paid.get("out_paid", 0) or 0)
        st.plotly_chart(
            free_vs_paid_chart(inc_free, inc_paid, out_free, out_paid),
            use_container_width=True,
        )
        st.dataframe(
            df_from_list([free_paid]), use_container_width=True, hide_index=True
        )
    else:
        empty_state("No distribution data.")
else:
    empty_state("Select season and competition for distribution.")

# Move Age vs Fee Profile to the end and format euros
st.subheader("Age vs Fee Profile")
age_fee = api.transfers_age_fee_profile()
age_fee_df = df_from_list(get_list(age_fee) or get_list(age_fee, key="buckets"))
if age_fee_df.empty:
    empty_state("No age/fee profile data.")
else:
    # Minimal columns
    keep = [
        c
        for c in ["age_bucket", "transfer_count", "avg_transfer_fee"]
        if c in age_fee_df.columns
    ]
    disp = age_fee_df[keep] if keep else age_fee_df
    try:
        fm = (
            {"avg_transfer_fee": _fmt_currency}
            if "avg_transfer_fee" in disp.columns
            else {}
        )
        st.dataframe(disp.style.format(fm), use_container_width=True, hide_index=True)
    except Exception:
        if "avg_transfer_fee" in disp.columns:
            disp["avg_transfer_fee"] = disp["avg_transfer_fee"].apply(_fmt_currency)
        st.dataframe(disp, use_container_width=True, hide_index=True)
