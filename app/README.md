# OpenFootball Streamlit App

A simple Streamlit UI to explore football data backed by the OpenFootball FastAPI service and DuckDB warehouse.

## Features
- League Overview: standings and league summary for a season/competition.
- Club Dashboard: club season performance and splits.
- Player Insights: search a player, view season per‑90 metrics, valuation trend, and career totals.
  - Competition filter: if none selected → shows overall season stats; if selected → shows league‑specific stats; if player didn’t play in that league → shows an info message and hides charts.
- Player Leaderboards: top players by metric (supports optional competition filter).
- Formations, Managers, Transfers, Market Movers: additional analyses and tables.

## Requirements
- Python 3.12
- Dependencies from `requirements.txt` (installed via `make setup`).
- Running API server (defaults to `http://localhost:8000`).
  - Configure via Streamlit secrets `api_base_url` or env var `OPENFOOTBALL_API_BASE`.

## Quick Start
1. Copy env: `cp .env.example .env`
2. Install deps and hooks: `make setup`
3. Run the API (in another terminal): `uvicorn api.app.main:app --reload`
4. Launch the app:
   - `make app` (recommended), or
   - `streamlit run app/Home.py`

## Usage
- Use the top filter bar to pick a Season and optionally a Competition.
- Player Insights:
  - Search and select a player to load metrics.
  - No competition selected → overall season metrics.
  - Competition selected → stats scoped to that league; if no appearances, you’ll see a small notice and charts are suppressed.
- Leaderboards support filtering by competition and minimum minutes.

## Notes
- Competition options are limited to domestic leagues and international cups to keep the list concise.
- Streamlit caches some API calls briefly (about 5 minutes). If options look stale, clear cache and rerun.

## Project Structure (app/)
- `Home.py`: entry point and navigation.
- `pages/`: individual views like League Overview, Player Insights, etc.
- `utils.py`: small UI/data helpers (filters, search select).
- `api_client.py`: tiny wrapper around the FastAPI endpoints.
- `charts.py`: Plotly chart helpers.

Enjoy exploring! If you want new views or metrics, open an issue or extend a page under `app/pages/`.
