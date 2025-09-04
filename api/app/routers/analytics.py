from typing import List, Optional, Literal
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from ..db import get_conn

router = APIRouter()


EFFICIENCY_METRICS = [
    "goals_per90",
    "assists_per90",
    "goal_plus_assist_per90",
    "efficiency_score",
]


class EfficiencyRow(BaseModel):
    player_id: int
    player_name: str
    age_in_season: Optional[int] = None
    minutes_played: int
    last_market_value: Optional[int] = None
    goals_per90: Optional[float] = None
    assists_per90: Optional[float] = None
    goal_plus_assist_per90: Optional[float] = None
    efficiency_score: Optional[float] = None


class AgeBucket(BaseModel):
    age_in_season: int
    player_count: int


@router.get(
    "/analytics/efficiency-screener",
    response_model=List[EfficiencyRow],
    response_model_exclude_none=True,
)
def efficiency_screener(
    season: str,
    min_minutes: int = Query(ge=0, default=0),
    value_max: Optional[int] = Query(default=None),
    metric: Literal[
        "goals_per90", "assists_per90", "goal_plus_assist_per90", "efficiency_score"
    ] = "efficiency_score",
    limit: int = Query(ge=1, le=500, default=100),
):
    """Screen players by efficiency metric with value and minutes filters."""
    if metric not in EFFICIENCY_METRICS:
        raise HTTPException(status_code=400, detail="Invalid metric")
    con = get_conn()
    q = f"""
    SELECT player_id, player_name, age_in_season, minutes_played,
           last_market_value, goals_per90, assists_per90, goal_plus_assist_per90, efficiency_score
    FROM mart_player_value_performance_corr
    WHERE season = ?
      AND minutes_played >= ?
      AND (? IS NULL OR last_market_value <= ?)
    ORDER BY {metric} DESC
    LIMIT ?
    """
    rows = con.execute(q, [season, min_minutes, value_max, value_max, limit]).fetchall()
    return [
        EfficiencyRow(
            player_id=r[0],
            player_name=r[1],
            age_in_season=r[2],
            minutes_played=r[3],
            last_market_value=r[4],
            goals_per90=r[5],
            assists_per90=r[6],
            goal_plus_assist_per90=r[7],
            efficiency_score=r[8],
        )
        for r in rows
    ]


@router.get(
    "/analytics/age-buckets",
    response_model=List[AgeBucket],
    response_model_exclude_none=True,
)
def age_buckets(season: str, competition_id: str):
    """Return age histogram for players in a competition and season."""
    con = get_conn()
    q = """
    SELECT v.age_in_season, COUNT(*) AS player_count
    FROM mart_player_value_performance_corr v
    JOIN mart_competition_club_season c USING (club_id, season)
    WHERE v.season = ? AND c.competition_id = ?
    GROUP BY v.age_in_season
    ORDER BY v.age_in_season
    """
    rows = con.execute(q, [season, competition_id]).fetchall()
    return [AgeBucket(age_in_season=r[0], player_count=r[1]) for r in rows]
