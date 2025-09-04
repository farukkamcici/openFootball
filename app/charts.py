from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


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
    # expects columns: matchday, points (or result value)
    if "matchday" not in df.columns:
        df["matchday"] = range(1, len(df) + 1)
    if "points" not in df.columns:
        df["points"] = 0
    fig = px.line(
        df,
        x="matchday",
        y="points",
        markers=True,
        color_discrete_sequence=[COLOR_PERF],
        template=PLOTLY_TEMPLATE,
    )
    fig.update_traces(mode="lines+markers", line=dict(width=2))
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=CARD_BG,
        xaxis=dict(gridcolor=GRID_COLOR),
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
