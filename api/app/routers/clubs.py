from fastapi import APIRouter, HTTPException, status
from typing import List
from pydantic import BaseModel
from ..db import get_conn

router = APIRouter()


class ClubSeason(BaseModel):
    club_name: str
    games_played: int
    wins: int
    draws: int
    losses: int
    points: int
    goals_for: int
    goals_against: int
    goal_difference: int
    squad_size: int
    squad_goals: int
    squad_assists: int
    squad_yellow_cards: int
    squad_red_cards: int


class ClubLeagueSplit(BaseModel):
    competition_id: str
    competition_name: str
    games_played: int
    wins: int
    draws: int
    losses: int
    points: int
    goals_for: int
    goals_against: int
    goal_difference: int


class ClubFormation(BaseModel):
    club_formation: str
    games_played: int
    wins: int
    draws: int
    losses: int
    ppg: float
    win_percentage: float
    goals_for: int
    goals_against: int


@router.get("/clubs/{club_id}/season", response_model=ClubSeason)
def club_season(club_id: int, season: str):
    """Return club season summary."""
    con = get_conn()
    q = """
    SELECT name, games_played, wins, draws, losses, points,
           goals_for, goals_against, goal_difference,
           squad_size, squad_goals, squad_assists, squad_yellow_cards, squad_red_cards
    FROM mart_club_season
    WHERE club_id = ? AND season = ?
    """
    r = con.execute(q, [club_id, season]).fetchone()
    if r is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Club season not found",
        )
    return ClubSeason(
        club_name=r[0],
        games_played=r[1],
        wins=r[2],
        draws=r[3],
        losses=r[4],
        points=r[5],
        goals_for=r[6],
        goals_against=r[7],
        goal_difference=r[8],
        squad_size=r[9],
        squad_goals=r[10],
        squad_assists=r[11],
        squad_yellow_cards=r[12],
        squad_red_cards=r[13],
    )


@router.get("/clubs/{club_id}/league-split", response_model=List[ClubLeagueSplit])
def club_league_split(club_id: int, season: str):
    """Return club performance split by competition."""
    con = get_conn()
    q = """
    SELECT competition_id, competition_name, games_played, wins, draws, losses,
           points, goals_for, goals_against, goal_difference
    FROM mart_competition_club_season
    WHERE club_id = ? AND season = ?
    ORDER BY points DESC
    """
    rows = con.execute(q, [club_id, season]).fetchall()
    return [
        ClubLeagueSplit(
            competition_id=r[0],
            competition_name=r[1],
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


class ClubHistoryRow(BaseModel):
    season: int
    points: int
    goals_for: int
    goals_against: int
    goal_difference: int


@router.get(
    "/clubs/{club_id}/history",
    response_model=List[ClubHistoryRow],
)
def club_history(club_id: int):
    """Return club season history for charting."""
    con = get_conn()
    q = """
    SELECT season, points, goals_for, goals_against, goal_difference
    FROM mart_club_season
    WHERE club_id = ?
    ORDER BY season
    """
    rows = con.execute(q, [club_id]).fetchall()
    return [
        ClubHistoryRow(
            season=r[0],
            points=r[1],
            goals_for=r[2],
            goals_against=r[3],
            goal_difference=r[4],
        )
        for r in rows
    ]


@router.get(
    "/clubs/{club_id}/history-competition",
    response_model=List[ClubHistoryRow],
)
def club_history_competition(club_id: int, competition_id: str):
    """Return club season history filtered by competition for charting."""
    con = get_conn()
    q = """
    SELECT season, points, goals_for, goals_against, goal_difference
    FROM mart_competition_club_season
    WHERE club_id = ? AND competition_id = ?
    ORDER BY season
    """
    rows = con.execute(q, [club_id, competition_id]).fetchall()
    return [
        ClubHistoryRow(
            season=r[0],
            points=r[1],
            goals_for=r[2],
            goals_against=r[3],
            goal_difference=r[4],
        )
        for r in rows
    ]


@router.get("/clubs/{club_id}/formations", response_model=List[ClubFormation])
def club_formations(club_id: int, season: str, competition_id: str):
    """Return club formation performance for given season and competition."""
    con = get_conn()
    q = """
    SELECT club_formation, games_played, wins, draws, losses, ppg, win_percentage,
           goals_for, goals_against
    FROM mart_club_formation_season
    WHERE club_id = ? AND season = ? AND competition_id = ?
    ORDER BY ppg DESC
    """
    rows = con.execute(q, [club_id, season, competition_id]).fetchall()
    return [
        ClubFormation(
            club_formation=r[0],
            games_played=r[1],
            wins=r[2],
            draws=r[3],
            losses=r[4],
            ppg=r[5],
            win_percentage=r[6],
            goals_for=r[7],
            goals_against=r[8],
        )
        for r in rows
    ]
