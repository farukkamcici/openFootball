import os
from typing import Any, Dict, Optional

import requests
import streamlit as st
import logging


_DEBUG = os.getenv("APP_DEBUG_HTTP", "0") in {"1", "true", "TRUE", "yes", "on"}
logger = logging.getLogger("app.api_client")


def _api_base_url() -> str:
    # Prefer Streamlit secrets, then env var, then default localhost
    try:
        val = st.secrets["api_base_url"]  # may raise if no secrets configured
        if val:
            return str(val).rstrip("/")
    except Exception:
        pass
    env = os.getenv("OPENFOOTBALL_API_BASE")
    if env:
        return str(env).rstrip("/")


def _headers() -> Dict[str, str]:
    return {"Accept": "application/json"}


def _url(path: str) -> str:
    base = _api_base_url()
    path = path if path.startswith("/") else f"/{path}"
    return f"{base}{path}"


def _safe_get(url: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict]:
    try:
        if _DEBUG:
            logger.warning("HTTP GET %s params=%s", url, params)
        resp = requests.get(url, params=params, headers=_headers(), timeout=20)
        if _DEBUG:
            logger.warning("HTTP %s -> %s", url, resp.status_code)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException:
        if _DEBUG:
            logger.exception("HTTP error for %s", url)
        return None


@st.cache_data(show_spinner=False, ttl=300)
def get_seasons() -> Optional[Dict]:
    return _safe_get(_url("/api/seasons"))


@st.cache_data(show_spinner=False, ttl=300)
def get_competitions() -> Optional[Dict]:
    return _safe_get(_url("/api/competitions"))


@st.cache_data(show_spinner=False, ttl=300)
def league_table(season: str, competition_id: str):
    return _safe_get(
        _url("/api/league-table"), {"season": season, "competition_id": competition_id}
    )


@st.cache_data(show_spinner=False, ttl=300)
def league_stats(season: str, competition_id: str):
    return _safe_get(
        _url("/api/league-stats"), {"season": season, "competition_id": competition_id}
    )


# Clubs
@st.cache_data(show_spinner=False, ttl=300)
def clubs_meta(competition_id: str, season: str):
    return _safe_get(
        _url("/api/meta/clubs"), {"competition_id": competition_id, "season": season}
    )


@st.cache_data(show_spinner=False, ttl=300)
def club_season(club_id: str, season: str) -> Optional[Dict]:
    return _safe_get(_url(f"/api/clubs/{club_id}/season"), {"season": season})


@st.cache_data(show_spinner=False, ttl=300)
def club_league_split(club_id: str, season: str) -> Optional[Dict]:
    return _safe_get(_url(f"/api/clubs/{club_id}/league-split"), {"season": season})


@st.cache_data(show_spinner=False, ttl=300)
def club_formations(club_id: str, season: str, competition_id: str):
    return _safe_get(
        _url(f"/api/clubs/{club_id}/formations"),
        {"season": season, "competition_id": competition_id},
    )


@st.cache_data(show_spinner=False, ttl=300)
def club_history(club_id: str) -> Optional[Dict]:
    return _safe_get(_url(f"/api/clubs/{club_id}/history"))


@st.cache_data(show_spinner=False, ttl=300)
def club_history_competition(club_id: str, competition_id: str) -> Optional[Dict]:
    return _safe_get(
        _url(f"/api/clubs/{club_id}/history-competition"),
        {"competition_id": competition_id},
    )


# Players
@st.cache_data(show_spinner=False, ttl=300)
def search_players(q: str) -> Optional[Dict]:
    return _safe_get(_url("/api/search/players"), {"q": q})


@st.cache_data(show_spinner=False, ttl=300)
def search_clubs(q: str) -> Optional[Dict]:
    return _safe_get(_url("/api/search/clubs"), {"q": q})


@st.cache_data(show_spinner=False, ttl=300)
def search_managers(q: str) -> Optional[Dict]:
    return _safe_get(_url("/api/search/managers"), {"q": q})


@st.cache_data(show_spinner=False, ttl=300)
def player_season(player_id: str, season: str) -> Optional[Dict]:
    return _safe_get(_url(f"/api/players/{player_id}/season"), {"season": season})


@st.cache_data(show_spinner=False, ttl=300)
def player_season_competition(
    player_id: str, season: str, competition_id: str
) -> Optional[Dict]:
    return _safe_get(
        _url(f"/api/players/{player_id}/season-competition"),
        {"season": season, "competition_id": competition_id},
    )


@st.cache_data(show_spinner=False, ttl=300)
def player_career(player_id: str) -> Optional[Dict]:
    return _safe_get(_url(f"/api/players/{player_id}/career"))


@st.cache_data(show_spinner=False, ttl=300)
def player_valuation_season(player_id: str, season: str) -> Optional[Dict]:
    return _safe_get(
        _url(f"/api/players/{player_id}/valuation-season"), {"season": season}
    )


@st.cache_data(show_spinner=False, ttl=300)
def player_valuation_history(player_id: str) -> Optional[Dict]:
    return _safe_get(_url(f"/api/players/{player_id}/valuation-history"))


@st.cache_data(show_spinner=False, ttl=300)
def players_top(
    season: str,
    metric: str = "goals",
    min_minutes: int = 600,
    limit: int = 50,
    competition: Optional[str] = None,
):
    params: Dict[str, Any] = {
        "season": season,
        "metric": metric,
        "min_minutes": min_minutes,
        "limit": limit,
    }
    if competition:
        params["competition_id"] = competition
    return _safe_get(_url("/api/players/top"), params)


# Note: /api/players/leaders not present; use players_top instead.


# Market
@st.cache_data(show_spinner=False, ttl=300)
def market_movers(season: str, direction: str = "up", limit: int = 50):
    return _safe_get(
        _url("/api/market/movers"),
        {"season": season, "direction": direction, "limit": limit},
    )


@st.cache_data(show_spinner=False, ttl=300)
def value_perf(season: str):
    return _safe_get(_url("/api/analytics/value-perf"), {"season": season})


# Formations
@st.cache_data(show_spinner=False, ttl=300)
def formations_league(season: str, competition_id: str):
    return _safe_get(
        _url("/api/formations/league"),
        {"season": season, "competition_id": competition_id},
    )


@st.cache_data(show_spinner=False, ttl=300)
def formations_history() -> Optional[Dict]:
    return _safe_get(_url("/api/formations/history"))


# Managers
@st.cache_data(show_spinner=False, ttl=300)
def managers_performance(limit: int = 100):
    return _safe_get(_url("/api/managers/performance"), {"limit": limit})


@st.cache_data(show_spinner=False, ttl=300)
def managers_formation(manager_name: str):
    return _safe_get(_url("/api/managers/formation"), {"manager_name": manager_name})


@st.cache_data(show_spinner=False, ttl=300)
def managers_best_formations() -> Optional[Dict]:
    return _safe_get(_url("/api/managers/best-formations"))


# Transfers
@st.cache_data(show_spinner=False, ttl=300)
def transfers_player(player_id: str) -> Optional[Dict]:
    return _safe_get(_url(f"/api/transfers/player/{player_id}"))


@st.cache_data(show_spinner=False, ttl=300)
def transfers_club(club_id: str, season: str) -> Optional[Dict]:
    return _safe_get(_url(f"/api/transfers/club/{club_id}"), {"season": season})


@st.cache_data(show_spinner=False, ttl=300)
def transfers_club_players(club_id: str, season: str) -> Optional[Dict]:
    return _safe_get(_url(f"/api/transfers/club/{club_id}/players"), {"season": season})


@st.cache_data(show_spinner=False, ttl=300)
def transfers_age_fee_profile() -> Optional[Dict]:
    return _safe_get(_url("/api/transfers/age-fee-profile"))


@st.cache_data(show_spinner=False, ttl=300)
def transfers_top_spenders(
    season: str, competition_id: str, limit: int = 20
) -> Optional[Dict]:
    params = {"season": season, "competition_id": competition_id, "limit": limit}
    return _safe_get(_url("/api/transfers/top-spenders"), params)


@st.cache_data(show_spinner=False, ttl=300)
def transfers_competition_summary(season: str) -> Optional[Dict]:
    return _safe_get(_url("/api/transfers/competition-summary"), {"season": season})


@st.cache_data(show_spinner=False, ttl=300)
def transfers_free_vs_paid(season: str, competition_id: str) -> Optional[Dict]:
    return _safe_get(
        _url("/api/transfers/free-vs-paid"),
        {"season": season, "competition_id": competition_id},
    )


# Compare
@st.cache_data(show_spinner=False, ttl=300)
def compare_players(ids: str, season: str) -> Optional[Dict]:
    """Compare players by metrics for a season.

    ids: comma-separated player_id list, e.g., "123,456,789"
    """
    return _safe_get(_url("/api/compare/players"), {"ids": ids, "season": season})


@st.cache_data(show_spinner=False, ttl=300)
def compare_clubs(ids: str, season: str) -> Optional[Dict]:
    """Compare clubs by season totals (aggregated across competitions)."""
    return _safe_get(_url("/api/compare/clubs"), {"ids": ids, "season": season})
