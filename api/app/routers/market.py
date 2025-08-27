from fastapi import APIRouter, Query
from typing import List, Optional, Literal, Annotated
from pydantic import BaseModel
from ..db import get_conn

router = APIRouter()


class MarketMover(BaseModel):
    player_id: int
    player_name: str
    first_market_value: int
    last_market_value: int
    value_change_amount: int
    value_change_percentage: float


class ValuePerf(BaseModel):
    player_id: int
    player_name: str
    age_in_season: Optional[int] = None
    minutes_played: int
    goals_per90: Optional[float] = None
    assists_per90: Optional[float] = None
    goal_plus_assist_per90: Optional[float] = None
    efficiency_score: Optional[float] = None
    first_market_value: Optional[int] = None
    last_market_value: Optional[int] = None
    value_change_amount: Optional[int] = None
    value_change_percentage: Optional[float] = None


@router.get("/market/movers", response_model=List[MarketMover])
def market_movers(
    season: str,
    direction: Literal["up", "down"] = "up",
    limit: Annotated[int, Query(ge=1, le=500)] = 50,
):
    """Return top value gainers or losers for given season."""
    con = get_conn()
    order = "DESC" if direction == "up" else "ASC"
    q = f"""
    SELECT player_id, name, first_market_value, last_market_value,
           value_change_amount, value_change_percentage
    FROM mart_player_valuation_season
    WHERE season = ?
    ORDER BY value_change_amount {order}
    LIMIT ?
    """
    rows = con.execute(q, [season, limit]).fetchall()
    return [
        MarketMover(
            player_id=r[0],
            player_name=r[1],
            first_market_value=r[2],
            last_market_value=r[3],
            value_change_amount=r[4],
            value_change_percentage=r[5],
        )
        for r in rows
    ]


@router.get("/analytics/value-perf", response_model=List[ValuePerf])
def value_perf(season: str):
    """Return value vs performance dataset for given season."""
    con = get_conn()
    q = """
    SELECT player_id, player_name, age_in_season, minutes_played,
           goals_per90, assists_per90, goal_plus_assist_per90, efficiency_score,
           first_market_value, last_market_value, value_change_amount, value_change_percentage
    FROM mart_player_value_performance_corr
    WHERE season = ?
    ORDER BY last_market_value DESC
    LIMIT 1000
    """
    rows = con.execute(q, [season]).fetchall()
    return [
        ValuePerf(
            player_id=r[0],
            player_name=r[1],
            age_in_season=r[2],
            minutes_played=r[3],
            goals_per90=r[4],
            assists_per90=r[5],
            goal_plus_assist_per90=r[6],
            efficiency_score=r[7],
            first_market_value=r[8],
            last_market_value=r[9],
            value_change_amount=r[10],
            value_change_percentage=r[11],
        )
        for r in rows
    ]
