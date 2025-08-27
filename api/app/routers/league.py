from fastapi import APIRouter, Query, HTTPException, status
from typing import List
from pydantic import BaseModel
from ..db import get_conn

router = APIRouter()


class LeagueRow(BaseModel):
    club_id: int
    club_name: str
    games_played: int
    wins: int
    draws: int
    losses: int
    points: int
    goals_for: int
    goals_against: int
    goal_difference: int


class LeagueStats(BaseModel):
    club_count: int
    avg_points: float
    avg_gd: float
    total_goals: int


@router.get("/league-table", response_model=List[LeagueRow])
def league_table(competition_id: str = Query(...), season: str = Query(...)):
    """Return league table for given competition and season."""
    con = get_conn()
    q = """
    SELECT club_id, club_name, games_played, wins, draws, losses,
           points, goals_for, goals_against, goal_difference
    FROM mart_competition_club_season
    WHERE competition_id = ? AND season = ?
    ORDER BY points DESC, goal_difference DESC
    """
    rows = con.execute(q, [competition_id, season]).fetchall()
    return [
        LeagueRow(
            club_id=r[0],
            club_name=r[1],
            games_played=r[2],
            wins=r[3],
            draws=r[4],
            losses=r[5],
            points=r[6],
            goals_for=r[7],
            goals_against=r[8],
            goal_difference=r[9],
        )
        for r in rows
    ]


@router.get("/league-stats", response_model=LeagueStats)
def league_stats(competition_id: str, season: str):
    """Return league summary stats for given competition and season."""
    con = get_conn()
    q = """
    SELECT
      COUNT(*) AS club_count,
      AVG(points) AS avg_points,
      AVG(goal_difference) AS avg_gd,
      SUM(goals_for) AS total_goals
    FROM mart_competition_club_season
    WHERE competition_id = ? AND season = ?
    """
    r = con.execute(q, [competition_id, season]).fetchone()
    # If no clubs found for given filters, return 404
    if r is None or (r[0] is not None and isinstance(r[0], int) and r[0] == 0):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League stats not found for given competition and season",
        )
    return LeagueStats(club_count=r[0], avg_points=r[1], avg_gd=r[2], total_goals=r[3])
