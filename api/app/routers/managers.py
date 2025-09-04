from fastapi import APIRouter, Query
from typing import Annotated
from typing import List
from pydantic import BaseModel
from ..db import get_conn

router = APIRouter()


class ManagerPerf(BaseModel):
    manager_name: str
    games_played: int
    points: int
    ppg: float
    win_rate: float


class ManagerFormation(BaseModel):
    club_formation: str
    games_played: int
    avg_goals_for: float
    avg_goals_against: float
    wins: int
    draws: int
    losses: int
    points: int
    ppg: float
    win_rate: float


@router.get("/managers/performance", response_model=List[ManagerPerf])
def manager_performance(limit: Annotated[int, Query(ge=1, le=500)] = 100):
    """Return manager performance for a season."""
    con = get_conn()
    q = """
    SELECT manager_name, games_played, points, ppg, win_rate
    FROM mart_manager_performance
    ORDER BY games_played DESC, ppg DESC
    LIMIT ?
    """
    rows = con.execute(q, [limit]).fetchall()
    return [
        ManagerPerf(
            manager_name=r[0], games_played=r[1], points=r[2], ppg=r[3], win_rate=r[4]
        )
        for r in rows
    ]


@router.get("/managers/formation", response_model=List[ManagerFormation])
def manager_formation(manager_name: str):
    """Return formation performance for a manager."""
    con = get_conn()
    q = """
    SELECT club_formation, games_played, avg_goals_for, avg_goals_against,
           wins, draws, losses, points, ppg, win_rate
    FROM mart_manager_formation_performance
    WHERE manager_name = ?
    ORDER BY ppg DESC
    """
    rows = con.execute(q, [manager_name]).fetchall()
    return [
        ManagerFormation(
            club_formation=r[0],
            games_played=r[1],
            avg_goals_for=r[2],
            avg_goals_against=r[3],
            wins=r[4],
            draws=r[5],
            losses=r[6],
            points=r[7],
            ppg=r[8],
            win_rate=r[9],
        )
        for r in rows
    ]


class ManagerBestFormation(BaseModel):
    manager_name: str
    club_formation: str
    ppg: float
    win_rate: float
    games_played: int


@router.get("/managers/best-formations", response_model=List[ManagerBestFormation])
def managers_best_formations(
    limit: Annotated[int, Query(ge=1, le=500)] = 50,
    min_games: Annotated[int, Query(ge=0)] = 10,
):
    """Return managers' best-performing formations ordered by PPG."""
    con = get_conn()
    q = """
    SELECT manager_name, club_formation, ppg, win_rate, games_played
    FROM mart_manager_formation_performance
    WHERE games_played >= ?
    ORDER BY ppg DESC
    LIMIT ?
    """
    rows = con.execute(q, [min_games, limit]).fetchall()
    return [
        ManagerBestFormation(
            manager_name=r[0],
            club_formation=r[1],
            ppg=r[2],
            win_rate=r[3],
            games_played=r[4],
        )
        for r in rows
    ]
