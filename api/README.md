# OpenFootball API

FastAPI service exposing read-only football data backed by DuckDB.

## Run Locally
- From repo root: `python -m api.startup_db && uvicorn api.app.main:app --reload`
- From `api/` dir: `python -m startup_db && uvicorn app.main:app --reload`
- Docs & try-it UI: `http://127.0.0.1:8000/docs`

Environment
- Required for serving: `ENV`, and one of `DEV_DB_PATH` or `PROD_DB_PATH` (picked by `ENV`).
- Optional for bootstrap: `RELEASE_DB_URL`, `RELEASE_DB_SHA256` for `python -m api.startup_db`.
- Note: `.env` files are NOT auto-loaded by uvicorn/FastAPI. Provide envs via your shell, platform, or `docker run --env-file`.

Docker
- Build: `docker build -t openfootball-api ./api`
- Run (with env file): `docker run --rm -p 8000:8000 --env-file api/.env openfootball-api`
- The container entrypoint runs: `python -m api.startup_db && uvicorn ...` so the DB is pulled on cold start.

Notes
- No authentication; all endpoints are GET and read-only.

Base URLs
- Health: `/health` and `/api/health`
- API: `/api/...`

## Endpoints
Meta
- GET `/api/seasons` — List available seasons.
  - Params: none
- GET `/api/competitions` — List available competitions.
  - Params: none
- GET `/api/meta/clubs` — Clubs within a competition and season.
  - Params: `competition_id` (str, required), `season` (str, required)

League
- GET `/api/league-table` — League table.
  - Params: `competition_id` (str, required), `season` (str, required)
- GET `/api/league-stats` — League summary.
  - Params: `competition_id` (str, required), `season` (str, required)
  - Success: 200 with aggregate fields
  - Errors: 404 if no clubs match the filters
  - Example: `curl "http://127.0.0.1:8000/api/league-stats?competition_id=GB1&season=2023"`

Search
- GET `/api/search/players` — Player autocomplete for season, enriched with career summary.
  - Params: `q` (str, required), `season` (str, required), `limit` (int, 1..100, default 20)
  - Returns: `player_id`, `player_name`, plus optional career totals from `mart_player_career_summary`:
    - `total_matches`, `total_minutes`, `total_goals`, `total_assists`, `total_goal_contributions`
    - `total_yellow_cards`, `total_red_cards`, per-game: `gpg`, `apg`, `total_goal_contributions_pg`
- GET `/api/search/clubs` — Club autocomplete within league and season, with aggregated career totals.
  - Params: `q` (str, required), `competition_id` (str, required), `season` (str, required), `limit` (int, 1..100, default 20)
  - Returns: `club_id`, `club_name`, plus totals aggregated across all seasons from `mart_club_season`:
    - `total_games_played`, `total_wins`, `total_draws`, `total_losses`, `total_points`
    - `total_goals_for`, `total_goals_against`, `total_goal_difference`

Compare
- GET `/api/compare/players` — Compare players by metrics.
  - Params: `ids` (csv of ints, required), `season` (str, required)
- GET `/api/compare/clubs` — Compare clubs within a league.
  - Params: `ids` (csv of ints, required), `season` (str, required), `competition_id` (str, required)

Clubs
- GET `/api/clubs/{club_id}/season` — Club season summary.
  - Params: `season` (str, required)
  - Errors: 404 if not found
  - Example: `curl "http://127.0.0.1:8000/api/clubs/985/season?season=2023"`
- GET `/api/clubs/{club_id}/league-split` — Club performance by competition.
  - Params: `season` (str, required)
- GET `/api/clubs/{club_id}/formations` — Club formation performance.
  - Params: `season` (str, required), `competition_id` (str, required)
- GET `/api/clubs/{club_id}/history` — Club season history (points/goals/GD).
  - Params: `metric` (str, optional; frontend only)

Players
- GET `/api/players/top` — Top players by metric.
  - Params: `season` (str, required), `metric` (enum), `min_minutes` (int, ge=0, default 600), `limit` (int, 1..500, default 50)
  - Example: `curl "http://127.0.0.1:8000/api/players/top?season=2023&metric=goals&min_minutes=600&limit=20"`
- GET `/api/players/{player_id}/season` — Player season stats.
  - Params: `season` (str, required)
  - Errors: 404 if not found
- GET `/api/players/{player_id}/valuation-season` — Player valuation deltas.
  - Params: `season` (str, required)
  - Errors: 404 if not found
- GET `/api/players/{player_id}/career` — Player season-by-season stats history.
  - Params: none
- GET `/api/players/{player_id}/valuation-history` — Player valuation trend by season.
  - Params: none
- GET `/api/players/leaders` — Leaders within a league/season by metric (club-independent).
  - Params: `season` (str, required), `competition_id` (str, required), `metric` (enum), `min_minutes` (int, ge=0, default 600), `limit` (int, 1..500, default 50)

Market & Analytics
- GET `/api/market/movers` — Value gainers/losers.
  - Params: `season` (str, required), `direction` (enum: up|down, default up), `limit` (int, 1..500, default 50)
  - Example: `curl "http://127.0.0.1:8000/api/market/movers?season=2023&direction=up&limit=25"`
- GET `/api/analytics/value-perf` — Value vs performance dataset.
  - Params: `season` (str, required)

Formations
- GET `/api/formations/league` — Formation performance for league.
  - Params: `competition_id` (str, required), `season` (str, required)
- GET `/api/formations/history` — Global formation performance history.
  - Params: none

Managers
- GET `/api/managers/performance` — Manager performance.
  - Params: `limit` (int, 1..500, default 100)
- GET `/api/managers/formation` — Manager formation performance.
  - Params: `manager_name` (str, required)
- GET `/api/managers/best-formations` — Best formations ordered by PPG.
  - Params: `season` (str, required), `limit` (int, 1..500, default 50)

Transfers
- GET `/api/transfers/player/{player_id}` — Player transfer history.
  - Params: none
- GET `/api/transfers/club/{club_id}` — Club transfer summary.
  - Params: `season` (str, required)
  - Errors: 404 if not found
  - Example: `curl "http://127.0.0.1:8000/api/transfers/club/985?season=2023"`
- GET `/api/transfers/age-fee-profile` — Transfer fee distribution by age bucket.
  - Params: none
- GET `/api/transfers/top-spenders` — Top net spenders in a league.
  - Params: `season` (str, required), `competition_id` (str, required), `limit` (int, default 20)
- GET `/api/transfers/competition-summary` — Transfer totals per competition.
  - Params: `season` (str, required)
- GET `/api/transfers/free-vs-paid` — Free vs paid transfer counts.
  - Params: `season` (str, required), `competition_id` (str, required)

System
- GET `/api/health` — API health probe.
- GET `/api/version` — Build version/time if available.
- GET `/api/limits` — API default limits.

## Errors & Conventions
- 200: Lists return empty arrays when no results.
- 404: Returned for single-resource lookups when not found.
- 400: Used sparingly for domain errors; most validation uses 422.
- 422: FastAPI validation errors (e.g., enum/constraints via Query or Literal).

## Examples
- `curl "http://127.0.0.1:8000/api/league-table?competition_id=GB1&season=2023"`
- `curl "http://127.0.0.1:8000/api/clubs/985/league-split?season=2023"`
- `curl "http://127.0.0.1:8000/api/formations/league?competition_id=GB1&season=2023"`
- `curl "http://127.0.0.1:8000/api/search/players?q=har&season=2023"`
- `curl "http://127.0.0.1:8000/api/compare/players?ids=44,123,456&season=2023"`
