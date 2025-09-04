from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from ..db import get_conn

router = APIRouter()


class ComparePlayer(BaseModel):
    player_id: int
    player_name: str
    minutes_played: int
    goals: int
    assists: int
    goals_per90: Optional[float] = None
    assists_per90: Optional[float] = None
    goal_plus_assist_per90: Optional[float] = None
    efficiency_score: Optional[float] = None
    season_last_value_eur: Optional[int] = None


class CompareClub(BaseModel):
    club_id: int
    club_name: str
    games_played: int
    points: int
    goals_for: int
    goals_against: int
    goal_difference: int


def _parse_ids(ids: Optional[str]) -> List[int]:
    if not ids:
        return []
    try:
        return [int(x) for x in ids.split(",") if x.strip()]
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid ids parameter; expected comma-separated integers",
        )


@router.get(
    "/compare/players",
    response_model=List[ComparePlayer],
    response_model_exclude_none=True,
)
def compare_players(ids: Optional[str] = Query(default=""), season: str = Query(...)):
    """Compare players by selected metrics for a season."""
    id_list = _parse_ids(ids)
    if not id_list:
        return []
    con = get_conn()
    placeholders = ",".join(["?"] * len(id_list))
    q = f"""
    SELECT player_id, player_name, minutes_played, goals, assists,
           goals_per90, assists_per90, goal_plus_assist_per90, efficiency_score,
           season_last_value_eur
    FROM mart_player_season
    WHERE season = ? AND player_id IN ({placeholders})
    ORDER BY player_name
    """
    params: List[object] = [season, *id_list]
    rows = con.execute(q, params).fetchall()
    return [
        ComparePlayer(
            player_id=r[0],
            player_name=r[1],
            minutes_played=r[2],
            goals=r[3],
            assists=r[4],
            goals_per90=r[5],
            assists_per90=r[6],
            goal_plus_assist_per90=r[7],
            efficiency_score=r[8],
            season_last_value_eur=r[9],
        )
        for r in rows
    ]


@router.get(
    "/compare/clubs",
    response_model=List[CompareClub],
    response_model_exclude_none=True,
)
def compare_clubs(ids: Optional[str] = Query(default=""), season: str = Query(...)):
    """Compare clubs within a competition for a season."""
    id_list = _parse_ids(ids)
    if not id_list:
        return []
    con = get_conn()
    placeholders = ",".join(["?"] * len(id_list))
    q = f"""
    SELECT club_id, club_name, games_played, points, goals_for, goals_against, goal_difference
    FROM mart_competition_club_season
    WHERE season = ? AND club_id IN ({placeholders})
    ORDER BY club_name
    """
    params: List[object] = [season, *id_list]
    rows = con.execute(q, params).fetchall()
    return [
        CompareClub(
            club_id=r[0],
            club_name=r[1],
            games_played=r[2],
            points=r[3],
            goals_for=r[4],
            goals_against=r[5],
            goal_difference=r[6],
        )
        for r in rows
    ]
