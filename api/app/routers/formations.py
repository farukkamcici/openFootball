from fastapi import APIRouter
from typing import List
from pydantic import BaseModel
from ..db import get_conn

router = APIRouter()


class LeagueFormation(BaseModel):
    club_formation: str
    games_played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    avg_goals_for: float
    avg_goals_against: float
    ppg: float
    win_percentage: float


@router.get("/formations/league", response_model=List[LeagueFormation])
def league_formations(competition_id: str, season: str):
    """Return formation performance for a league and season."""
    con = get_conn()
    q = """
    SELECT club_formation, games_played, wins, draws, losses,
           goals_for, goals_against, avg_goals_for, avg_goals_against, ppg, win_percentage
    FROM mart_competition_formation_season
    WHERE competition_id = ? AND season = ?
    ORDER BY games_played DESC, ppg DESC
    """
    rows = con.execute(q, [competition_id, season]).fetchall()
    return [
        LeagueFormation(
            club_formation=r[0],
            games_played=r[1],
            wins=r[2],
            draws=r[3],
            losses=r[4],
            goals_for=r[5],
            goals_against=r[6],
            avg_goals_for=r[7],
            avg_goals_against=r[8],
            ppg=r[9],
            win_percentage=r[10],
        )
        for r in rows
    ]


@router.get("/formations/history", response_model=List[LeagueFormation])
def formation_history():
    """Return global formation performance history."""
    con = get_conn()
    q = """
    SELECT club_formation, games_played, wins, draws, losses,
           goals_for, goals_against, avg_goals_for, avg_goals_against, ppg, win_percentage
    FROM mart_formation_history_performance
    ORDER BY games_played DESC, ppg DESC
    """
    rows = con.execute(q).fetchall()
    return [
        LeagueFormation(
            club_formation=r[0],
            games_played=r[1],
            wins=r[2],
            draws=r[3],
            losses=r[4],
            goals_for=r[5],
            goals_against=r[6],
            avg_goals_for=r[7],
            avg_goals_against=r[8],
            ppg=r[9],
            win_percentage=r[10],
        )
        for r in rows
    ]
