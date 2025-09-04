import streamlit as st
import os
import sys

_CUR_DIR = os.path.dirname(__file__)
_APP_ROOT = os.path.dirname(_CUR_DIR)
if _APP_ROOT not in sys.path:
    sys.path.insert(0, _APP_ROOT)

try:
    from app import api_client as api
    from app.charts import scatter_perf_vs_value
    from app.utils import (
        df_from_list,
        empty_state,
        get_list,
        filter_bar,
        inject_theme,
        section_tabs,
    )
except ModuleNotFoundError:
    import api_client as api
    from charts import scatter_perf_vs_value
    from utils import (
        df_from_list,
        empty_state,
        get_list,
        filter_bar,
        inject_theme,
        section_tabs,
    )


inject_theme()
st.title("Market Movers")
season, _competition = filter_bar(
    include_season=True, include_competition=False, key_prefix="market_movers"
)

if not season:
    empty_state("Select a season to view market movers.")
    st.stop()


def _as_list(payload):
    return payload if isinstance(payload, list) else get_list(payload)


# Controls for movers
ctrl_cols = st.columns([2, 3, 7])
with ctrl_cols[0]:
    direction = st.radio(
        "Direction",
        ["down", "up"],
        index=0,
        horizontal=True,
        key="market_movers_direction",
    )
with ctrl_cols[1]:
    limit = st.slider("Limit", 10, 200, 50, 10, key="market_movers_limit")

raw = api.market_movers(season, direction=direction, limit=limit) or []
raw_perf = api.value_perf(season) or []

movers_df = df_from_list(_as_list(raw))
value_perf = df_from_list(_as_list(raw_perf))

if not movers_df.empty and "value_change_amount" in movers_df.columns:
    movers_df = movers_df.sort_values(
        by="value_change_amount", ascending=(direction == "down"), kind="mergesort"
    )

tab_movers, tab_perf = section_tabs(["Movers", "Perf vs Value"], key="market_tabs")

with tab_movers:
    st.subheader(f"Top {'Losers' if direction=='down' else 'Gainers'}")

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

    if movers_df.empty:
        alt = value_perf.copy()
        if alt.empty:
            opp = "up" if direction == "down" else "down"
            opp_raw = api.market_movers(season, direction=opp, limit=limit) or []
            opp_df = df_from_list(_as_list(opp_raw))
            if opp_df.empty:
                empty_state("No movers for selected filters.")
            else:
                empty_state(
                    f"No {'gainers' if direction=='up' else 'losers'} for this season. Try switching to {opp}."
                )
        else:
            if "value_change_amount" not in alt.columns:
                if {"first_market_value", "last_market_value"}.issubset(
                    set(alt.columns)
                ):
                    alt["value_change_amount"] = alt["last_market_value"].fillna(
                        0
                    ) - alt["first_market_value"].fillna(0)
                else:
                    alt["value_change_amount"] = 0
            asc = True if direction == "down" else False
            alt = alt.sort_values(by="value_change_amount", ascending=asc)
            display_cols = [
                c
                for c in [
                    "player_name",
                    "first_market_value",
                    "last_market_value",
                    "value_change_amount",
                    "value_change_percentage",
                ]
                if c in alt.columns
            ]
            alt = alt[display_cols].head(limit)
            if alt.empty:
                empty_state("No movers for selected filters.")
            else:
                # Format money-like columns in Euros
                money_cols = [
                    c
                    for c in [
                        "first_market_value",
                        "last_market_value",
                        "value_change_amount",
                    ]
                    if c in alt.columns
                ]
                try:
                    fmt_map = {c: _fmt_currency for c in money_cols}
                    st.dataframe(
                        alt.style.format(fmt_map),
                        use_container_width=True,
                        hide_index=True,
                    )
                except Exception:
                    for c in money_cols:
                        alt[c] = alt[c].apply(_fmt_currency)
                    st.dataframe(alt, use_container_width=True, hide_index=True)
    else:
        # Show main movers table with Euro formatting
        money_cols = [
            c
            for c in [
                "first_market_value",
                "last_market_value",
                "value_change_amount",
            ]
            if c in movers_df.columns
        ]
        try:
            fmt_map = {c: _fmt_currency for c in money_cols}
            st.dataframe(
                movers_df.style.format(fmt_map),
                use_container_width=True,
                hide_index=True,
            )
        except Exception:
            df2 = movers_df.copy()
            for c in money_cols:
                df2[c] = df2[c].apply(_fmt_currency)
            st.dataframe(df2, use_container_width=True, hide_index=True)

with tab_perf:
    st.subheader("Performance vs Value Delta")
    perf_df = value_perf.copy()
    if perf_df.empty:
        empty_state("No value-performance data.")
    else:
        colset = set(perf_df.columns)
        if "player_name" in colset:
            perf_df = perf_df.rename(columns={"player_name": "label"})
        if "efficiency_score" in colset:
            perf_df = perf_df.rename(columns={"efficiency_score": "performance"})
        elif "goal_plus_assist_per90" in colset:
            perf_df = perf_df.rename(columns={"goal_plus_assist_per90": "performance"})
        elif "goals_per90" in colset:
            perf_df = perf_df.rename(columns={"goals_per90": "performance"})
        else:
            perf_df["performance"] = 0
        if "value_change_amount" in colset:
            perf_df = perf_df.rename(columns={"value_change_amount": "value_delta"})
        elif {"first_market_value", "last_market_value"}.issubset(colset):
            perf_df["value_delta"] = perf_df["last_market_value"].fillna(0) - perf_df[
                "first_market_value"
            ].fillna(0)
        elif "last_market_value" in colset:
            perf_df["value_delta"] = perf_df["last_market_value"].fillna(0)
        else:
            perf_df["value_delta"] = 0

        st.plotly_chart(
            scatter_perf_vs_value(perf_df),
            use_container_width=True,
            key="market_perf_vs_value",
        )
