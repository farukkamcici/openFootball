# OpenFootball

End-to-end, local-first football analytics stack built on DuckDB, dbt, and Streamlit. It ingests a Kaggle dataset, converts CSV → Parquet, loads into DuckDB, runs dbt models with tests, stream on FastAPI and serves a Streamlit app.

## Quickstart

- Prereqs: Python 3.12, pip, Make, Kaggle CLI configured (`~/.kaggle/kaggle.json`).
- Bootstrap:
  1) `cp .env.example .env`
  2) `make setup`
  3) `make ingest` (downloads Kaggle dataset to `data/raw/<timestamp>`)
  4) `make parquet` (CSV → Parquet into `data/parquet/<timestamp>`)
  5) `make warehouse` (loads Parquet into `warehouse/transfermarkt.duckdb`)
  6) `make dbt` (runs models + schema tests)
  7) `make app` (runs Streamlit; expects `app/Home.py`)

Use `make run` for end-to-end: ingest → parquet → warehouse → dbt → dq → app.

## Project Structure

- `ingest/`: Raw → Parquet scripts (e.g., `csv_to_parquet.py`).
- `warehouse/`: DuckDB loader and artifacts (`load_duckdb.py`, `warehouse/*.duckdb`).
- `transform/`: dbt project (`dbt_project.yml`, `models/`, `macros/`, `target/`).
- `api/`: FastAPI service (`api/app/main.py`, routers in `api/app/routers/`). See `api/README.md`.
- `app/`: Streamlit app (entry: `app/Home.py`). See `app/README.md`.
- `data/`: Raw and Parquet data controlled by `.env` (`RAW_DIR`, `PARQUET_DIR`, `DATA_DIR`).
- `quality/`, `docs/`, `ops/`: Reserved for data quality, docs, and ops glue.

## Make Targets

- `make setup`: Install Python deps and pre-commit hooks.
- `make ingest`: Download Kaggle dataset → `data/raw/<timestamp>` (requires `.env` + Kaggle CLI).
- `make parquet`: Convert latest raw CSVs → Parquet in `data/parquet/<timestamp>`.
- `make warehouse`: Load Parquet into DuckDB at `warehouse/transfermarkt.duckdb`.
- `make dbt`: Run dbt models and schema tests using the `transform/` profile.
- `make dq`: Placeholder for Great Expectations checkpoints.
- `make app`: Launch Streamlit locally.
- `make run`: End-to-end: ingest → parquet → warehouse → dbt → dq → app.

API helpers
- `make api`: Start FastAPI with uvicorn (dev reload).
- `make startup-db`: Ensure serving DuckDB exists from release envs.
- `make smoke`: Hit a few endpoints against `OPENFOOTBALL_API_BASE`.

Helpful: `make help` prints available targets.

## API

- Run locally: `uvicorn api.app.main:app --reload` (from repo root) or `uvicorn app.main:app --reload` (from `api/`).
- Docs UI: `http://127.0.0.1:8000/docs`.
- CORS: set `CORS_ALLOW_ORIGINS` (comma-separated) when serving the app from another origin.
- DuckDB (serving): for production-like serving, see `python -m api.startup_db` in `DEPLOY.md` and use `ENV`, `DEV_DB_PATH`/`PROD_DB_PATH`, `RELEASE_DB_URL`, `RELEASE_DB_SHA256`.
- Details and endpoints: see `api/README.md`.

## Configuration (.env)

Copy `.env.example` to `.env` and adjust as needed:

```
DATA_DIR=./data
PARQUET_DIR=./data/parquet
RAW_DIR=./data/raw
DUCKDB_PATH=./warehouse/transfermarkt.duckdb
KAGGLE_DATASET=davidcariboo/player-scores
```

- Kaggle CLI must be configured before `make ingest` (`~/.kaggle/kaggle.json`).
- After `make ingest`, a timestamp is written to `data/LATEST` to drive downstream steps.

## Development

- Python 3.12. Format with Black (88 cols) and lint with Ruff (pre-commit configured).
- Scripts are single-purpose; use snake_case for modules, functions, variables.
- Run `pre-commit run -a` before committing.

## dbt Project

- Profile name: `openfootball_duckdb` (configured under `transform/`).
- Staging models under `transform/models/stg/` are prefixed `stg_` and materialized as views.
- Source declarations in `transform/models/src/` (e.g., `src_transfermarkt.yaml`).
- Mart models under `transform/models/mart/` with schema tests in `mart_schema.yml`.
- Run with `make dbt` (equivalent to `dbt run && dbt test --profiles-dir transform`).

## Data Quality

- dbt schema tests defined under `transform/models/**/schema.yml`.

## Streamlit App

- `make app` runs `streamlit run app/Home.py`.
- The app talks to the API at `OPENFOOTBALL_API_BASE` (env) or `st.secrets["OPENFOOTBALL_API_BASE"]`; defaults to `http://localhost:8000`.

## Troubleshooting

- Missing `.env`: copy from example: `cp .env.example .env`.
- `RAW_DIR not set` or `KAGGLE_DATASET not set`: ensure vars exist in `.env`.
- `Run 'make ingest' first (no LATEST)`: perform ingest to create `data/LATEST`.
- Kaggle download errors: verify CLI auth (`kaggle datasets list`), dataset name, and network access.

## Contributing

- Commits: short, imperative tense (e.g., "Initialize dbt", "Add DuckDB loader").
- PRs: include purpose, key changes, linked issues, and verification notes (row counts, sample queries, screenshots). Mention impacted `make` targets and `.env` changes.
- Before opening a PR: run `pre-commit run -a` and `make dbt`.

For full contributor guidance, see `AGENTS.md`.

## Credits & Data

- Data source: Kaggle dataset referenced by `KAGGLE_DATASET` (default: `davidcariboo/player-scores`).
- Never commit secrets; `.env` is gitignored.
