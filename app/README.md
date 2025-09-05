# OpenFootball Streamlit App

Streamlit UI for exploring football data backed by the OpenFootball FastAPI and DuckDB warehouse. It provides league, club, player, transfer, and analytics views with interactive filters and Plotly charts.

## Requirements
- Python 3.12
- Install deps: `make setup`
- Running API server: defaults to `http://localhost:8000`
  - Configure via Streamlit secrets `api_base_url` or env var `OPENFOOTBALL_API_BASE`

## Quick Start
1) Project setup
- `cp .env.example .env`
- `make setup`

2) Run API (separate terminal)
- `uvicorn app.main:app --reload` from `api/` or `uvicorn api.app.main:app --reload` from repo root

3) Launch Streamlit
- `make app` or `streamlit run app/Home.py`

Tip: set `OPENFOOTBALL_API_BASE` to your API URL (e.g., `export OPENFOOTBALL_API_BASE=http://127.0.0.1:8000`).

## Configuration
- Base URL order of precedence:
  1. `st.secrets["api_base_url"]`
  2. `OPENFOOTBALL_API_BASE` env var
  3. `http://localhost:8000`
- Streamlit caching: responses cached for ~5 minutes via `@st.cache_data(ttl=300)`.

## App Navigation and Pages
- `Home`: Quick links to all sections.
- `Leagues` (pages/1_Leagues.py)
  - Select season and competition; view table and summary stats.
  - Endpoints: `/api/seasons`, `/api/competitions`, `/api/league-table`, `/api/league-stats`.
- `Clubs` (pages/2_Clubs.py)
  - Club season overview, league split, formations, history.
  - Endpoints: `/api/meta/clubs`, `/api/clubs/{id}/season`, `/api/clubs/{id}/league-split`, `/api/clubs/{id}/formations`, `/api/clubs/{id}/history`, `/api/clubs/{id}/history-competition`.
- `Players` (pages/3_Players.py)
  - Tabs: Career, Season, Value vs Performance.
  - Career: totals (games, minutes, goals, assists) and valuation by season chart.
    - Uses: `/api/players/{player_id}/career`, `/api/players/{player_id}/valuation-history`.
  - Season: season summary metrics plus Per90 bar (Goals/90, Assists/90, G+A/90).
    - Uses: `/api/players/{player_id}/season` or `/api/players/{player_id}/season-competition` when a league is selected.
  - Value vs Performance: dual-axis chart with selectable metrics.
    - Performance options: G+A, G+A/90, Goals/90, Assists/90, Efficiency.
    - Value options: Last value, Max value, YoY delta, YoY %.
    - Uses: `/api/players/{player_id}/career`, `/api/players/{player_id}/valuation-history`.
- `Player Leaderboards` (pages/4_Player_Leaderboards.py)
  - Top players by metric with min minutes and optional league filter.
  - Endpoint: `/api/players/top`.
- `Formations` (pages/5_Formations.py)
  - League formations by season and history.
  - Endpoints: `/api/formations/league`, `/api/formations/history`.
- `Managers` (pages/6_Managers.py)
  - Performance table and best formations.
  - Endpoints: `/api/managers/performance`, `/api/managers/best-formations`, `/api/managers/formation`.
- `Transfers` (pages/7_Transfers.py)
  - Club transfers, free vs paid, top spenders, age-fee profile.
  - Endpoints: `/api/transfers/club/{id}`, `/api/transfers/club/{id}/players`, `/api/transfers/free-vs-paid`, `/api/transfers/top-spenders`, `/api/transfers/competition-summary`, `/api/transfers/age-fee-profile`, `/api/transfers/player/{player_id}`.
- `Market Movers` (pages/8_Market_Movers.py)
  - Biggest value risers/fallers.
  - Endpoint: `/api/market/movers`.
- `Compare` (pages/9_Compare.py)
  - Compare multiple players or clubs side-by-side.
  - Endpoints: `/api/compare/players`, `/api/compare/clubs`.

## Charts and Visualizations
- Plotly-based charts in `app/charts.py` with dark theme.
- Common helpers:
  - `per90_bar(goals90, assists90, ga90)` — Per-90 metrics bar.
  - `valuation_trend(df, x, y)` — valuation lines with currency formatting.
  - `value_vs_performance_dual(df, x_col, value_col, perf_col, ...)` — dual-axis market value vs performance.
  - Plus utilities: histograms, scatter plots, radar compare.

## API Reference (Used by the App)
- Meta: `/api/seasons`, `/api/competitions`
- Search: `/api/search/players`, `/api/search/clubs`, `/api/search/managers`
- Leagues: `/api/league-table`, `/api/league-stats`
- Clubs: `/api/meta/clubs`, `/api/clubs/{id}/season`, `/api/clubs/{id}/league-split`, `/api/clubs/{id}/formations`, `/api/clubs/{id}/history`, `/api/clubs/{id}/history-competition`
- Players: `/api/players/{id}/season`, `/api/players/{id}/season-competition`, `/api/players/{id}/career`, `/api/players/{id}/valuation-history`, `/api/players/top`
- Formations: `/api/formations/league`, `/api/formations/history`
- Managers: `/api/managers/performance`, `/api/managers/formation`, `/api/managers/best-formations`
- Transfers: `/api/transfers/player/{id}`, `/api/transfers/club/{id}`, `/api/transfers/club/{id}/players`, `/api/transfers/free-vs-paid`, `/api/transfers/top-spenders`, `/api/transfers/competition-summary`, `/api/transfers/age-fee-profile`
- Market: `/api/market/movers`
- Compare: `/api/compare/players`, `/api/compare/clubs`


## Troubleshooting
- If the app can’t reach the API, set `OPENFOOTBALL_API_BASE` or `st.secrets["api_base_url"]`.
- Clear Streamlit cache if filters or options look stale: “Clear cache” → Rerun.
- Value vs Performance requires both career and valuation data; if one is missing, you’ll see a friendly empty state.

## Folder Structure (app/)
- `Home.py`: Streamlit entry and navigation.
- `pages/`: individual views (1_Leagues, 2_Clubs, 3_Players, ...).
- `api_client.py`: HTTP client for the FastAPI endpoints with caching.
- `charts.py`: central Plotly chart helpers (dark theme).
- `utils.py`: shared UI/data utilities (filters, search select, tabs, empty states).

Contributions welcome — add or tweak views under `app/pages/` and keep things single-purpose and composable.
