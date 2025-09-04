from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional, Literal, Annotated
from pydantic import BaseModel
from ..db import get_conn

router = APIRouter()


class PlayerTop(BaseModel):
    player_id: int
    player_name: str
    games_played: int
    minutes_played: int
    goals: int
    assists: int
    total_goals_and_assists: int
    yellow_cards: int
    red_cards: int
    goals_per90: Optional[float] = None
    assists_per90: Optional[float] = None
    goal_plus_assist_per90: Optional[float] = None
    efficiency_score: Optional[float] = None


class PlayerSeason(BaseModel):
    player_name: str
    games_played: int
    minutes_played: int
    goals: int
    assists: int
    yellow_cards: int
    red_cards: int
    goals_per90: Optional[float] = None
    assists_per90: Optional[float] = None
    goal_plus_assist_per90: Optional[float] = None
    efficiency_score: Optional[float] = None
    season_last_value_eur: int


class PlayerValuationSeason(BaseModel):
    first_market_value: int
    last_market_value: int
    min_market_value: int
    max_market_value: int
    value_change_amount: int
    value_change_percentage: float


@router.get("/players/top", response_model=List[PlayerTop])
def players_top(
    season: str,
    metric: Literal[
        "minutes_played",
        "goals",
        "assists",
        "total_goals_and_assists",
        "yellow_cards",
        "red_cards",
        "goals_per90",
        "assists_per90",
        "goal_plus_assist_per90",
        "efficiency_score",
    ],
    min_minutes: Annotated[int, Query(ge=0)] = 600,
    limit: Annotated[int, Query(ge=1, le=500)] = 50,
):
    """Return top players by given metric and season."""
    con = get_conn()
    q = f"""
    SELECT player_id, player_name, games_played, minutes_played,
           goals, assists, (goals + assists) AS total_goals_and_assists,
           yellow_cards, red_cards,
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
            goals=r[4],
            assists=r[5],
            total_goals_and_assists=r[6],
            yellow_cards=r[7],
            red_cards=r[8],
            goals_per90=r[9],
            assists_per90=r[10],
            goal_plus_assist_per90=r[11],
            efficiency_score=r[12],
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
    if r is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player season not found",
        )
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
    if r is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player valuation season not found",
        )
    return PlayerValuationSeason(
        first_market_value=r[0],
        last_market_value=r[1],
        min_market_value=r[2],
        max_market_value=r[3],
        value_change_amount=r[4],
        value_change_percentage=r[5],
    )


class PlayerCareerRow(BaseModel):
    season: int
    games_played: int
    minutes_played: int
    goals: int
    assists: int
    goals_per90: Optional[float] = None
    assists_per90: Optional[float] = None
    goal_plus_assist_per90: Optional[float] = None
    efficiency_score: Optional[float] = None
    season_last_value_eur: Optional[int] = None


@router.get(
    "/players/{player_id}/career",
    response_model=List[PlayerCareerRow],
    response_model_exclude_none=True,
)
def player_career(player_id: int):
    """Return player season-by-season performance history."""
    con = get_conn()
    q = """
    SELECT season, games_played, minutes_played, goals, assists,
           goals_per90, assists_per90, goal_plus_assist_per90, efficiency_score,
           season_last_value_eur
    FROM mart_player_season
    WHERE player_id = ?
    ORDER BY season
    """
    rows = con.execute(q, [player_id]).fetchall()
    return [
        PlayerCareerRow(
            season=r[0],
            games_played=r[1],
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


class PlayerValuationHistoryRow(BaseModel):
    season: str
    first_market_value: int
    last_market_value: int
    min_market_value: int
    max_market_value: int


@router.get(
    "/players/{player_id}/valuation-history",
    response_model=List[PlayerValuationHistoryRow],
)
def player_valuation_history(player_id: int):
    """Return market value trend by season for a player."""
    con = get_conn()
    q = """
    SELECT season, first_market_value, last_market_value, min_market_value, max_market_value
    FROM mart_player_valuation_season
    WHERE player_id = ?
    ORDER BY season
    """
    rows = con.execute(q, [player_id]).fetchall()
    return [
        PlayerValuationHistoryRow(
            season=r[0],
            first_market_value=r[1],
            last_market_value=r[2],
            min_market_value=r[3],
            max_market_value=r[4],
        )
        for r in rows
    ]


LEADER_METRICS = [
    "minutes_played",
    "goals",
    "assists",
    "goal_plus_assist_per90",
    "goals_per90",
    "assists_per90",
    "efficiency_score",
]


class PlayerLeaderRow(BaseModel):
    player_id: int
    player_name: str
    minutes_played: int
    goals: int
    assists: int
    goals_per90: Optional[float] = None
    assists_per90: Optional[float] = None
    goal_plus_assist_per90: Optional[float] = None
    efficiency_score: Optional[float] = None


@router.get(
    "/players/leaders",
    response_model=List[PlayerLeaderRow],
    response_model_exclude_none=True,
)
def player_leaders(
    season: str,
    competition_id: str,
    metric: Literal[
        "minutes_played",
        "goals",
        "assists",
        "goal_plus_assist_per90",
        "goals_per90",
        "assists_per90",
        "efficiency_score",
    ],
    min_minutes: int = Query(ge=0, default=0),
    limit: int = Query(ge=1, le=500, default=50),
):
    """Return leaders by metric for a season and competition (club-independent)."""
    if metric not in LEADER_METRICS:
        raise HTTPException(status_code=400, detail="Invalid metric")
    con = get_conn()
    q = f"""
    SELECT player_id, player_name, minutes_played, goals, assists,
           goals_per90, assists_per90, goal_plus_assist_per90, efficiency_score
    FROM mart_competition_player_season
    WHERE season = ?
      AND competition_id = ?
      AND minutes_played >= ?
    ORDER BY {metric} DESC
    LIMIT ?
    """
    rows = con.execute(q, [season, competition_id, min_minutes, limit]).fetchall()
    return [
        PlayerLeaderRow(
            player_id=r[0],
            player_name=r[1],
            minutes_played=r[2],
            goals=r[3],
            assists=r[4],
            goals_per90=r[5],
            assists_per90=r[6],
            goal_plus_assist_per90=r[7],
            efficiency_score=r[8],
        )
        for r in rows
    ]
