from fastapi import APIRouter
from typing import List
from pydantic import BaseModel
from ..db import get_conn

router = APIRouter()


class PlayerTop(BaseModel):
    player_id: int
    player_name: str
    games_played: int
    minutes_played: int
    goals_per90: float
    assists_per90: float
    goal_plus_assist_per90: float
    efficiency_score: float


class PlayerSeason(BaseModel):
    player_name: str
    games_played: int
    minutes_played: int
    goals: int
    assists: int
    yellow_cards: int
    red_cards: int
    goals_per90: float
    assists_per90: float
    goal_plus_assist_per90: float
    efficiency_score: float
    season_last_value_eur: int


class PlayerValuationSeason(BaseModel):
    first_market_value: int
    last_market_value: int
    min_market_value: int
    max_market_value: int
    value_change_amount: int
    value_change_percentage: float


@router.get("/players/top", response_model=List[PlayerTop])
def players_top(season: str, metric: str, min_minutes: int = 600, limit: int = 50):
    """Return top players by given metric and season."""
    allowed = [
        "goals_per90",
        "assists_per90",
        "goal_plus_assist_per90",
        "efficiency_score",
    ]
    if metric not in allowed:
        raise ValueError("Invalid metric")
    con = get_conn()
    q = f"""
    SELECT player_id, player_name, games_played, minutes_played,
           goals_per90, assists_per90, goal_plus_assist_per90, efficiency_score
    FROM mart_player_season
    WHERE season = ? AND minutes_played >= ?
    ORDER BY {metric} DESC
    LIMIT ?
    """
    rows = con.execute(q, [season, min_minutes, limit]).fetchall()
    return [
        PlayerTop(
            player_id=r[0],
            player_name=r[1],
            games_played=r[2],
            minutes_played=r[3],
            goals_per90=r[4],
            assists_per90=r[5],
            goal_plus_assist_per90=r[6],
            efficiency_score=r[7],
        )
        for r in rows
    ]


@router.get("/players/{player_id}/season", response_model=PlayerSeason)
def player_season(player_id: int, season: str):
    """Return player stats for given season."""
    con = get_conn()
    q = """
    SELECT player_name, games_played, minutes_played, goals, assists,
           yellow_cards, red_cards,
           goals_per90, assists_per90, goal_plus_assist_per90, efficiency_score,
           season_last_value_eur
    FROM mart_player_season
    WHERE player_id = ? AND season = ?
    """
    r = con.execute(q, [player_id, season]).fetchone()
    return PlayerSeason(
        player_name=r[0],
        games_played=r[1],
        minutes_played=r[2],
        goals=r[3],
        assists=r[4],
        yellow_cards=r[5],
        red_cards=r[6],
        goals_per90=r[7],
        assists_per90=r[8],
        goal_plus_assist_per90=r[9],
        efficiency_score=r[10],
        season_last_value_eur=r[11],
    )


@router.get(
    "/players/{player_id}/valuation-season", response_model=PlayerValuationSeason
)
def valuation_season(player_id: int, season: str):
    """Return player valuation changes for given season."""
    con = get_conn()
    q = """
    SELECT first_market_value, last_market_value, min_market_value, max_market_value,
           value_change_amount, value_change_percentage
    FROM mart_player_valuation_season
    WHERE player_id = ? AND season = ?
    """
    r = con.execute(q, [player_id, season]).fetchone()
    return PlayerValuationSeason(
        first_market_value=r[0],
        last_market_value=r[1],
        min_market_value=r[2],
        max_market_value=r[3],
        value_change_amount=r[4],
        value_change_percentage=r[5],
    )
