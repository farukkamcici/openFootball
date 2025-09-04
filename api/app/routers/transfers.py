from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from ..db import get_conn
from datetime import date

router = APIRouter()


class TransferPlayer(BaseModel):
    transfer_date: date
    season: str
    from_club_id: int
    from_club_name: str
    to_club_id: int
    to_club_name: str
    is_free_transfer: bool
    is_loan_out: bool
    is_loan_return: bool
    market_value_in_eur: Optional[int]
    transfer_fee: int
    fee_norm: float
    transfer_category: str


class TransferClub(BaseModel):
    club_name: str
    incoming_total: int
    outgoing_total: int
    incoming_free_cnt: int
    incoming_paid_cnt: int
    incoming_loan_cnt: int
    incoming_loan_return_cnt: int
    outgoing_free_cnt: int
    outgoing_paid_cnt: int
    outgoing_loan_cnt: int
    outgoing_loan_return_cnt: int
    transfer_spend: int
    transfer_income: int
    net_spend: int
    incoming_free_rate: float
    incoming_paid_rate: float
    outgoing_paid_rate: float


class AgeFeeProfile(BaseModel):
    age_bucket: str
    transfer_count: int
    avg_transfer_fee: float


@router.get("/transfers/player/{player_id}", response_model=List[TransferPlayer])
def player_transfers(player_id: int):
    """Return player transfer history."""
    con = get_conn()
    q = """
    SELECT transfer_date, season, from_club_id, from_club_name,
           to_club_id, to_club_name, is_free_transfer, is_loan_out, is_loan_return,
           market_value_in_eur, transfer_fee, fee_norm, transfer_category
    FROM mart_transfer_player
    WHERE player_id = ?
    ORDER BY transfer_date DESC
    """
    rows = con.execute(q, [player_id]).fetchall()
    return [
        TransferPlayer(
            transfer_date=r[0],
            season=r[1],
            from_club_id=r[2],
            from_club_name=r[3],
            to_club_id=r[4],
            to_club_name=r[5],
            is_free_transfer=r[6],
            is_loan_out=r[7],
            is_loan_return=r[8],
            market_value_in_eur=r[9],
            transfer_fee=r[10],
            fee_norm=r[11],
            transfer_category=r[12],
        )
        for r in rows
    ]


@router.get("/transfers/club/{club_id}", response_model=TransferClub)
def club_transfers(club_id: int, season: str):
    """Return club transfer summary for a season."""
    con = get_conn()
    q = """
    SELECT club_name, incoming_total, outgoing_total,
           incoming_free_cnt, incoming_paid_cnt, incoming_loan_cnt, incoming_loan_return_cnt,
           outgoing_free_cnt, outgoing_paid_cnt, outgoing_loan_cnt, outgoing_loan_return_cnt,
           transfer_spend, transfer_income, net_spend,
           incoming_free_rate, incoming_paid_rate, outgoing_paid_rate
    FROM mart_transfer_club
    WHERE club_id = ? AND season = ?
    """
    r = con.execute(q, [club_id, season]).fetchone()
    if r is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Club transfer summary not found for given season",
        )
    return TransferClub(
        club_name=r[0],
        incoming_total=r[1],
        outgoing_total=r[2],
        incoming_free_cnt=r[3],
        incoming_paid_cnt=r[4],
        incoming_loan_cnt=r[5],
        incoming_loan_return_cnt=r[6],
        outgoing_free_cnt=r[7],
        outgoing_paid_cnt=r[8],
        outgoing_loan_cnt=r[9],
        outgoing_loan_return_cnt=r[10],
        transfer_spend=r[11],
        transfer_income=r[12],
        net_spend=r[13],
        incoming_free_rate=r[14],
        incoming_paid_rate=r[15],
        outgoing_paid_rate=r[16],
    )


@router.get("/transfers/age-fee-profile", response_model=List[AgeFeeProfile])
def age_fee_profile():
    """Return transfer fee distribution by age bucket."""
    con = get_conn()
    q = """
    SELECT age_bucket, transfer_count, avg_transfer_fee
    FROM mart_transfer_age_fee_profile
    ORDER BY age_bucket
    """
    rows = con.execute(q).fetchall()
    return [
        AgeFeeProfile(age_bucket=r[0], transfer_count=r[1], avg_transfer_fee=r[2])
        for r in rows
    ]


class TransferSpendRow(BaseModel):
    club_id: int
    club_name: str
    transfer_spend: int
    transfer_income: int
    net_spend: int


@router.get(
    "/transfers/top-spenders",
    response_model=List[TransferSpendRow],
)
def top_spenders(season: str, competition_id: str, limit: int = 20):
    """Return top net spenders for a competition and season."""
    con = get_conn()
    q = """
    SELECT t.club_id, c.club_name, t.transfer_spend, t.transfer_income, t.net_spend
    FROM mart_transfer_club t
    JOIN mart_competition_club_season c
      ON c.club_id = t.club_id
     AND LEFT(t.season, 4) = c.season
    WHERE t.season = ? AND c.competition_id = ?
    ORDER BY t.net_spend DESC
    LIMIT ?
    """
    rows = con.execute(q, [season, competition_id, limit]).fetchall()
    return [
        TransferSpendRow(
            club_id=r[0],
            club_name=r[1],
            transfer_spend=r[2],
            transfer_income=r[3],
            net_spend=r[4],
        )
        for r in rows
    ]


class CompetitionTransferSummary(BaseModel):
    competition_id: str
    competition_name: str
    total_spend: int
    total_income: int
    total_net: int


@router.get(
    "/transfers/competition-summary",
    response_model=List[CompetitionTransferSummary],
)
def competition_summary(season: str):
    """Return transfer spend/income totals per competition for a season."""
    con = get_conn()
    q = """
    SELECT c.competition_id, c.competition_name,
           SUM(t.transfer_spend) AS total_spend,
           SUM(t.transfer_income) AS total_income,
           SUM(t.net_spend) AS total_net
    FROM mart_transfer_club t
    JOIN mart_competition_club_season c
    ON c.club_id = t.club_id
    AND LEFT(t.season, 4) = c.season
    WHERE t.season = ?
    GROUP BY c.competition_id, c.competition_name
    ORDER BY total_net DESC
    """
    rows = con.execute(q, [season]).fetchall()
    return [
        CompetitionTransferSummary(
            competition_id=r[0],
            competition_name=r[1],
            total_spend=r[2],
            total_income=r[3],
            total_net=r[4],
        )
        for r in rows
    ]


class FreeVsPaid(BaseModel):
    inc_free: int
    inc_paid: int
    out_free: int
    out_paid: int


@router.get(
    "/transfers/free-vs-paid",
    response_model=FreeVsPaid,
)
def free_vs_paid(season: str, competition_id: str):
    """Return free vs paid transfer counts aggregated for a competition and season."""
    con = get_conn()
    q = """
    SELECT
      SUM(t.incoming_free_cnt) AS inc_free,
      SUM(t.incoming_paid_cnt) AS inc_paid,
      SUM(t.outgoing_free_cnt) AS out_free,
      SUM(t.outgoing_paid_cnt) AS out_paid
    FROM mart_transfer_club t
    JOIN mart_competition_club_season c
    ON c.club_id = t.club_id
    AND LEFT(t.season, 4) = c.season
    WHERE t.season = ? AND c.competition_id = ?
    """
    r = con.execute(q, [season, competition_id]).fetchone()
    if r is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No data found"
        )
    return FreeVsPaid(inc_free=r[0], inc_paid=r[1], out_free=r[2], out_paid=r[3])
