from fastapi import APIRouter, Query
from typing import List, Annotated
from pydantic import BaseModel
from ..db import get_conn

router = APIRouter()


class PlayerSearch(BaseModel):
    player_id: int
    player_name: str
    total_matches: int | None = None
    total_minutes: int | None = None
    total_goals: int | None = None
    total_assists: int | None = None
    total_goal_contributions: int | None = None
    total_yellow_cards: int | None = None
    total_red_cards: int | None = None
    gpg: float | None = None
    apg: float | None = None
    total_goal_contributions_pg: float | None = None


class ClubSearch(BaseModel):
    club_id: int
    club_name: str
    total_games_played: int | None = None
    total_wins: int | None = None
    total_draws: int | None = None
    total_losses: int | None = None
    total_points: int | None = None
    total_goals_for: int | None = None
    total_goals_against: int | None = None
    total_goal_difference: int | None = None


@router.get(
    "/search/players",
    response_model=List[PlayerSearch],
    response_model_exclude_none=True,
)
def search_players(
    q: str,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    """Player autocomplete for a season with career summary fields."""
    con = get_conn()
    qsql = """
        WITH candidates AS (
            SELECT DISTINCT player_id
            FROM mart_player_season
            WHERE player_name ILIKE '%' || ? || '%'
            LIMIT ?
        )
        SELECT pcs.player_id,
               pcs.player_name,
               pcs.total_matches,
               pcs.total_minutes,
               pcs.total_goals,
               pcs.total_assists,
               pcs.total_goal_contributions,
               pcs.total_yellow_cards,
               pcs.total_red_cards,
               pcs.gpg,
               pcs.apg,
               pcs.total_goal_contributions_pg
        FROM mart_player_career_summary pcs
        JOIN candidates c
          ON pcs.player_id = c.player_id
        ORDER BY pcs.player_name
        """
    rows = con.execute(qsql, [q, limit]).fetchall()
    return [
        PlayerSearch(
            player_id=r[0],
            player_name=r[1],
            total_matches=r[2],
            total_minutes=r[3],
            total_goals=r[4],
            total_assists=r[5],
            total_goal_contributions=r[6],
            total_yellow_cards=r[7],
            total_red_cards=r[8],
            gpg=r[9],
            apg=r[10],
            total_goal_contributions_pg=r[11],
        )
        for r in rows
    ]


@router.get(
    "/search/clubs",
    response_model=List[ClubSearch],
    response_model_exclude_none=True,
)
def search_clubs(
    q: str,
    competition_id: str,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    """Club autocomplete within competition and season with aggregated career totals."""
    con = get_conn()
    qsql = """
        WITH candidates AS (
            SELECT DISTINCT club_id, club_name
            FROM mart_competition_club_season
            WHERE competition_id = ?
              AND club_name ILIKE '%' || ? || '%'
            ORDER BY club_name
            LIMIT ?
        ),
        agg AS (
            SELECT club_id,
                   SUM(games_played)      AS total_games_played,
                   SUM(wins)              AS total_wins,
                   SUM(draws)             AS total_draws,
                   SUM(losses)            AS total_losses,
                   SUM(points)            AS total_points,
                   SUM(goals_for)         AS total_goals_for,
                   SUM(goals_against)     AS total_goals_against,
                   SUM(goal_difference)   AS total_goal_difference
            FROM mart_competition_club_season
            WHERE competition_id = ?
            GROUP BY club_id
        )
        SELECT c.club_id,
               c.club_name,
               COALESCE(a.total_games_played, 0),
               COALESCE(a.total_wins, 0),
               COALESCE(a.total_draws, 0),
               COALESCE(a.total_losses, 0),
               COALESCE(a.total_points, 0),
               COALESCE(a.total_goals_for, 0),
               COALESCE(a.total_goals_against, 0),
               COALESCE(a.total_goal_difference, 0)
        FROM candidates c
        LEFT JOIN agg a USING (club_id)
        ORDER BY c.club_name
        """
    rows = con.execute(qsql, [competition_id, q, limit, competition_id]).fetchall()
    return [
        ClubSearch(
            club_id=r[0],
            club_name=r[1],
            total_games_played=r[2],
            total_wins=r[3],
            total_draws=r[4],
            total_losses=r[5],
            total_points=r[6],
            total_goals_for=r[7],
            total_goals_against=r[8],
            total_goal_difference=r[9],
        )
        for r in rows
    ]
