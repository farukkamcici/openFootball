# OpenFootball API

FastAPI service exposing read-only football data backed by DuckDB (`warehouse/transfermarkt.duckdb`).

## Run Locally
- From repo root: `uvicorn api.app.main:app --reload`
- From `api/` dir: `uvicorn app.main:app --reload`
- Docs & try-it UI: `http://127.0.0.1:8000/docs`

Notes
- Default DB path: `warehouse/transfermarkt.duckdb` (override with env `LOCAL_DB_PATH`).
- No authentication; all endpoints are GET and read-only.

Base URLs
- Health: `/health`
- API: `/api/...`

## Endpoints
Meta
- GET `/api/seasons` — List available seasons.
  - Params: none
- GET `/api/competitions` — List available competitions.
  - Params: none

League
- GET `/api/league-table` — League table.
  - Params: `competition_id` (str, required), `season` (str, required)
- GET `/api/league-stats` — League summary.
  - Params: `competition_id` (str, required), `season` (str, required)
  - Success: 200 with aggregate fields
  - Errors: 404 if no clubs match the filters
  - Example: `curl "http://127.0.0.1:8000/api/league-stats?competition_id=GB1&season=2023"`

Clubs
- GET `/api/clubs/{club_id}/season` — Club season summary.
  - Params: `season` (str, required)
  - Errors: 404 if not found
  - Example: `curl "http://127.0.0.1:8000/api/clubs/985/season?season=2023"`
- GET `/api/clubs/{club_id}/league-split` — Club performance by competition.
  - Params: `season` (str, required)
- GET `/api/clubs/{club_id}/formations` — Club formation performance.
  - Params: `season` (str, required), `competition_id` (str, required)

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

Transfers
- GET `/api/transfers/player/{player_id}` — Player transfer history.
  - Params: none
- GET `/api/transfers/club/{club_id}` — Club transfer summary.
  - Params: `season` (str, required)
  - Errors: 404 if not found
  - Example: `curl "http://127.0.0.1:8000/api/transfers/club/985?season=2023"`
- GET `/api/transfers/age-fee-profile` — Transfer fee distribution by age bucket.
  - Params: none

## Errors & Conventions
- 200: Lists return empty arrays when no results.
- 404: Returned for single-resource lookups when not found.
- 400: Used sparingly for domain errors; most validation uses 422.
- 422: FastAPI validation errors (e.g., enum/constraints via Query or Literal).

## Examples
- `curl "http://127.0.0.1:8000/api/league-table?competition_id=GB1&season=2023"`
- `curl "http://127.0.0.1:8000/api/clubs/985/league-split?season=2023"`
- `curl "http://127.0.0.1:8000/api/formations/league?competition_id=GB1&season=2023"`
