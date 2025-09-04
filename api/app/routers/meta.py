from fastapi import APIRouter
from typing import List
from pydantic import BaseModel
from ..db import get_conn

router = APIRouter()


class SeasonOut(BaseModel):
    season: int


class CompetitionOut(BaseModel):
    competition_id: str
    competition_name: str


@router.get("/seasons", response_model=List[SeasonOut])
def seasons():
    """Return all available seasons."""
    con = get_conn()
    q = """
    SELECT DISTINCT season
    FROM mart_competition_club_season
    ORDER BY season DESC
    """
    rows = con.execute(q).fetchall()
    return [SeasonOut(season=r[0]) for r in rows]


@router.get("/competitions", response_model=List[CompetitionOut])
def competitions():
    """Return competitions."""
    con = get_conn()
    q = """
    SELECT DISTINCT m.competition_id, m.competition_name
    FROM mart_competition_club_season m
    JOIN main_stg.stg_competitions s
    ON s.competition_id = m.competition_id
    WHERE s.competition_type IN ('domestic_league', 'international_cup')
    ORDER BY m.competition_name
    """
    rows = con.execute(q).fetchall()
    return [CompetitionOut(competition_id=r[0], competition_name=r[1]) for r in rows]


class ClubLite(BaseModel):
    club_id: int
    club_name: str


@router.get(
    "/clubs",
    response_model=List[ClubLite],
    response_model_exclude_none=True,
)
def clubs(competition_id: str, season: str):
    """Return clubs for a competition and season (non-autocomplete)."""
    con = get_conn()
    q = """
    SELECT DISTINCT club_id, club_name
    FROM mart_competition_club_season
    WHERE competition_id = ? AND season = ?
    ORDER BY club_name
    """
    rows = con.execute(q, [competition_id, season]).fetchall()
    return [ClubLite(club_id=r[0], club_name=r[1]) for r in rows]
