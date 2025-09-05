from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


PLOTLY_TEMPLATE = "plotly_dark"
COLOR_PERF = "#2991FF"  # blue
COLOR_GAIN = "#21BA45"  # green
COLOR_LOSS = "#DB2828"  # red
GRID_COLOR = "rgba(255,255,255,0.08)"
BG_COLOR = "#0E1117"
CARD_BG = "#111827"


def scatter_points_vs_gd(df: pd.DataFrame) -> go.Figure:
    cols = {"points": "points", "gd": "gd", "club": "club"}
    for k in cols.values():
        if k not in df.columns:
            df[k] = None
    fig = px.scatter(
        df,
        x="gd",
        y="points",
        hover_name="club",
        color_discrete_sequence=[COLOR_PERF],
        template=PLOTLY_TEMPLATE,
    )
    fig.update_traces(marker=dict(size=10, opacity=0.9))
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=CARD_BG,
        xaxis=dict(gridcolor=GRID_COLOR, zeroline=False),
        yaxis=dict(gridcolor=GRID_COLOR, zeroline=False),
    )
    return fig


def histogram_goals(df: pd.DataFrame, column: str = "goals") -> go.Figure:
    if column not in df.columns:
        df[column] = []
    fig = px.histogram(
        df,
        x=column,
        nbins=20,
        color_discrete_sequence=[COLOR_PERF],
        template=PLOTLY_TEMPLATE,
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=CARD_BG,
        xaxis=dict(gridcolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR),
        bargap=0.08,
    )
    return fig


def results_trendline(df: pd.DataFrame) -> go.Figure:
    # Prefer season on x-axis if present; fallback to matchday
    x_col = "season" if "season" in df.columns else "matchday"
    if x_col not in df.columns:
        df[x_col] = range(1, len(df) + 1)
    if "points" not in df.columns:
        df["points"] = 0

    # If seasons present, impose chronological order on x-axis
    if x_col == "season":

        def _season_key(s: object) -> int:
            try:
                s_str = str(s)
                # Extract first 4-digit year as start
                import re

                m = re.search(r"(19|20)\d{2}", s_str)
                if m:
                    return int(m.group(0))
                # Fallback: numeric cast
                return int(float(s_str))
            except Exception:
                return 0

        unique_seasons = list(pd.unique(df[x_col]))
        ordered = sorted(unique_seasons, key=_season_key)
        try:
            df[x_col] = pd.Categorical(df[x_col], categories=ordered, ordered=True)
        except Exception:
            pass

    fig = px.line(
        df,
        x=x_col,
        y="points",
        markers=True,
        color_discrete_sequence=[COLOR_PERF],
        template=PLOTLY_TEMPLATE,
    )
    fig.update_traces(mode="lines+markers", line=dict(width=2))
    # Label x-axis depending on the data
    xaxis_title = "Season" if x_col == "season" else "Matchday"
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=CARD_BG,
        xaxis=dict(gridcolor=GRID_COLOR, title=xaxis_title),
        yaxis=dict(gridcolor=GRID_COLOR),
    )
    return fig


def sparkline(
    df: pd.DataFrame, x: str, y: str, color: Optional[str] = None
) -> go.Figure:
    color_seq = [color or COLOR_PERF]
    fig = px.line(
        df, x=x, y=y, template=PLOTLY_TEMPLATE, color_discrete_sequence=color_seq
    )
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=100,
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=CARD_BG,
    )
    return fig


def valuation_trend(
    df: pd.DataFrame, x: str, y: str, title: Optional[str] = None
) -> go.Figure:
    # Clean, readable valuation trend with axes and currency formatting
    fig = px.line(
        df,
        x=x,
        y=y,
        markers=True,
        template=PLOTLY_TEMPLATE,
        color_discrete_sequence=[COLOR_PERF],
        title=title,
    )
    fig.update_traces(mode="lines+markers", line=dict(width=3))
    fig.update_layout(
        margin=dict(l=10, r=10, t=30 if title else 10, b=10),
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=CARD_BG,
        xaxis=dict(gridcolor=GRID_COLOR, title=x, showline=False, zeroline=False),
        yaxis=dict(
            gridcolor=GRID_COLOR,
            title="Market Value",
            tickformat=",.0f",
        ),
        hovermode="x unified",
    )
    return fig


def scatter_perf_vs_value(df: pd.DataFrame) -> go.Figure:
    # expects columns: performance, value_delta, label
    for c in ["performance", "value_delta", "label"]:
        if c not in df.columns:
            df[c] = None
    fig = px.scatter(
        df,
        x="performance",
        y="value_delta",
        hover_name="label",
        color_discrete_sequence=[COLOR_PERF],
        template=PLOTLY_TEMPLATE,
    )
    fig.update_traces(marker=dict(size=10, opacity=0.9))
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=CARD_BG,
        xaxis=dict(gridcolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR),
    )
    return fig


def per90_bar(goals90: float, assists90: float, ga90: float) -> go.Figure:
    data = pd.DataFrame(
        {
            "metric": ["Goals/90", "Assists/90", "G+A/90"],
            "value": [goals90 or 0.0, assists90 or 0.0, ga90 or 0.0],
        }
    )
    fig = px.bar(
        data,
        x="metric",
        y="value",
        color="metric",
        color_discrete_sequence=[COLOR_GAIN, COLOR_PERF, COLOR_LOSS],
        template=PLOTLY_TEMPLATE,
    )
    fig.update_layout(
        showlegend=False,
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=CARD_BG,
        xaxis=dict(gridcolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR),
    )
    fig.update_traces(marker_line_width=0, opacity=0.95)
    return fig


def top_spenders_bar(df: pd.DataFrame) -> go.Figure:
    # expects columns: club_name, net_spend
    if "club_name" not in df.columns:
        df["club_name"] = ""
    if "net_spend" not in df.columns:
        df["net_spend"] = 0
    data = df.sort_values(by="net_spend", ascending=False).copy()
    fig = px.bar(
        data,
        x="club_name",
        y="net_spend",
        template=PLOTLY_TEMPLATE,
        color_discrete_sequence=[COLOR_PERF],
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=20, b=60),
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=CARD_BG,
        xaxis=dict(gridcolor=GRID_COLOR, tickangle=45),
        yaxis=dict(gridcolor=GRID_COLOR, title="Net Spend"),
        showlegend=False,
    )
    return fig


def free_vs_paid_chart(
    inc_free: int, inc_paid: int, out_free: int, out_paid: int
) -> go.Figure:
    data = pd.DataFrame(
        {
            "movement": ["Incoming", "Incoming", "Outgoing", "Outgoing"],
            "type": ["Free", "Paid", "Free", "Paid"],
            "count": [inc_free or 0, inc_paid or 0, out_free or 0, out_paid or 0],
        }
    )
    fig = px.bar(
        data,
        x="movement",
        y="count",
        color="type",
        barmode="stack",
        template=PLOTLY_TEMPLATE,
        color_discrete_sequence=[COLOR_GAIN, COLOR_PERF],
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=CARD_BG,
        xaxis=dict(gridcolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR, title="Transfers"),
    )
    return fig


def fee_timeline(
    df: pd.DataFrame,
    x: str = "transfer_date",
    y: str = "transfer_fee",
    title: Optional[str] = None,
) -> go.Figure:
    # Nicer fee timeline with currency formatting and markers
    data = df.copy()
    if x not in data.columns:
        data[x] = range(1, len(data) + 1)
    if y not in data.columns:
        data[y] = 0
    fig = px.line(
        data,
        x=x,
        y=y,
        markers=True,
        template=PLOTLY_TEMPLATE,
        color_discrete_sequence=[COLOR_PERF],
        title=title,
    )
    fig.update_traces(mode="lines+markers", line=dict(width=3))
    fig.update_layout(
        margin=dict(l=10, r=10, t=30 if title else 10, b=10),
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=CARD_BG,
        xaxis=dict(gridcolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR, title="Transfer Fee", tickformat=",.0f"),
        hovermode="x unified",
    )
    return fig


def radar_compare(
    df: pd.DataFrame,
    categories: list[str],
    name_col: str,
    title: Optional[str] = None,
    radial_range: Optional[tuple[float, float]] = None,
    height: int = 460,
    rotation: int = 90,
    showlegend: bool = False,
) -> go.Figure:
    """Generic radar chart comparing rows over given categories.

    Expects numeric columns for categories and a label column `name_col`.
    """
    if df is None or df.empty:
        df = pd.DataFrame(columns=[name_col] + categories)
    fig = go.Figure()
    for _, row in df.iterrows():
        values = [float(row.get(c) or 0.0) for c in categories]
        fig.add_trace(
            go.Scatterpolar(
                r=values,
                theta=categories,
                fill="toself",
                name=str(row.get(name_col, "")),
            )
        )
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=BG_COLOR,
        polar=dict(
            bgcolor=CARD_BG,
            radialaxis=dict(visible=True, gridcolor=GRID_COLOR),
            angularaxis=dict(
                gridcolor=GRID_COLOR,
                rotation=rotation,
                direction="clockwise",
                tickfont=dict(size=12),
            ),
        ),
        showlegend=showlegend,
        margin=dict(l=64, r=64, t=36 if title else 12, b=32),
        title=title,
        height=height,
    )
    if radial_range is not None:
        fig.update_polars(radialaxis=dict(range=list(radial_range)))
    return fig


def value_vs_performance_dual(
    df: pd.DataFrame,
    x_col: str = "season",
    value_col: str = "value",
    perf_col: str = "performance",
    value_name: str = "Market Value",
    perf_name: str = "Performance",
) -> go.Figure:
    """Dual-axis chart: value (line) vs performance (area).

    Expects df with x_col, value_col, perf_col. X is typically season.
    """
    data = (
        df.copy()
        if df is not None
        else pd.DataFrame(columns=[x_col, value_col, perf_col])
    )
    for c in [x_col, value_col, perf_col]:
        if c not in data.columns:
            data[c] = []

    # Order seasons chronologically if using season on x-axis
    if x_col == "season":

        def _season_key(s: object) -> int:
            try:
                s_str = str(s)
                import re

                m = re.search(r"(19|20)\d{2}", s_str)
                return int(m.group(0)) if m else int(float(s_str))
            except Exception:
                return 0

        # Filter out null/blank season labels from categories to avoid pandas errors
        unique_seasons = [
            s for s in pd.unique(data[x_col]) if pd.notna(s) and str(s).strip() != ""
        ]
        ordered = sorted(unique_seasons, key=_season_key)
        try:
            data[x_col] = pd.Categorical(data[x_col], categories=ordered, ordered=True)
        except Exception:
            pass

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Value line on primary axis
    fig.add_trace(
        go.Scatter(
            x=data[x_col],
            y=data[value_col],
            mode="lines+markers",
            name=value_name,
            line=dict(color=COLOR_PERF, width=3),
            marker=dict(size=6),
        ),
        secondary_y=False,
    )

    # Performance area on secondary axis
    fig.add_trace(
        go.Scatter(
            x=data[x_col],
            y=data[perf_col],
            mode="lines",
            name=perf_name,
            line=dict(color=COLOR_GAIN, width=2),
            fill="tozeroy",
            fillcolor="rgba(33,186,69,0.25)",
        ),
        secondary_y=True,
    )

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=CARD_BG,
        margin=dict(l=10, r=10, t=30, b=10),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    fig.update_xaxes(
        title_text="Season" if x_col == "season" else x_col, gridcolor=GRID_COLOR
    )
    fig.update_yaxes(title_text="Market Value", gridcolor=GRID_COLOR, secondary_y=False)
    fig.update_yaxes(title_text="Performance", gridcolor=GRID_COLOR, secondary_y=True)
    return fig
