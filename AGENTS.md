# Repository Guidelines

## Project Structure & Module Organization
- `ingest/`: Raw → Parquet utilities (e.g., `csv_to_parquet.py`).
- `warehouse/`: DuckDB loader and artifacts (`load_duckdb.py`, `warehouse/transfermarkt.duckdb`).
- `transform/`: dbt project (`dbt_project.yml`, `models/`, `macros/`, `target/`).
- `api/`: FastAPI service (`api/app/main.py`, routers in `api/app/routers/`).
- `app/`: Streamlit UI entry (`app/Home.py`).
- `data/`: Managed by `.env` (`RAW_DIR`, `PARQUET_DIR`, `DATA_DIR`).
- `quality/`, `docs/`, `ops/`: Reserved for data quality, docs, and ops glue.

## Build, Test, and Development Commands
- `make setup`: Install Python deps and pre-commit hooks.
- `make ingest`: Download Kaggle dataset → `data/raw/<timestamp>` (requires `.env` + Kaggle CLI).
- `make parquet`: Convert latest raw CSVs → `data/parquet/<timestamp>`.
- `make warehouse`: Load Parquet into DuckDB at `warehouse/transfermarkt.duckdb`.
- `make dbt`: Run dbt models and schema tests using the `transform/` profile.
- `make dq`: Run data quality checks (Great Expectations placeholder).
- `make app`: Launch Streamlit locally; entry is `app/Home.py`.
- `make run`: End-to-end pipeline: ingest → parquet → warehouse → dbt → dq → app.
Example: `cp .env.example .env && make setup && make ingest`.

## Coding Style & Naming Conventions
- Python 3.12. Format with Black (88 cols) and lint with Ruff (via pre-commit).
- Use `snake_case` for modules, functions, and variables; keep scripts single-purpose.
- dbt: stage models prefixed `stg_` under `transform/models/stg/`; macros in `transform/macros/`.

## Testing Guidelines
- dbt tests: define in `transform/models/**/schema.yml`; run with `make dbt`.
- Data quality: integrate Great Expectations; execute with `make dq` when available.
- Sanity checks: run scripts directly (e.g., `python ingest/csv_to_parquet.py SRC DST`).

## Commit & Pull Request Guidelines
- Commits: short, imperative (e.g., "Initialize dbt", "Add DuckDB loader").
- PRs: describe purpose, key changes, linked issues, and verification (row counts, sample queries, Streamlit screenshots). Mention impacted `make` targets and any `.env` updates.
- Before opening a PR: run `pre-commit run -a` and `make dbt`.

## Security & Configuration Tips
- Copy `.env.example` to `.env`; set `DATA_DIR`, `RAW_DIR`, `PARQUET_DIR`, `DUCKDB_PATH`, `KAGGLE_DATASET`.
- Configure Kaggle CLI (`~/.kaggle/kaggle.json`) before `make ingest`.
- Do not commit secrets; `.env` is gitignored.
