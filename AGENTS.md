# Repository Guidelines

This guide helps contributors work efficiently in this repository. It summarizes structure, commands, style, testing, and PR expectations.

## Project Structure & Module Organization
- `ingest/`: Raw → Parquet scripts (e.g., `csv_to_parquet.py`).
- `warehouse/`: DuckDB loader and artifacts (`load_duckdb.py`, `warehouse/*.duckdb`).
- `transform/`: dbt project (`dbt_project.yml`, `models/`, `macros/`, `target/`).
- `app/`: Streamlit app entrypoint (`make app` expects `app/Home.py`).
- `data/`: Raw and Parquet data managed by `.env` (`RAW_DIR`, `PARQUET_DIR`, `DATA_DIR`).
- `quality/`, `docs/`, `ops/`: Reserved for data quality, docs, and ops glue.

## Build, Test, and Development Commands
- `make setup`: Install Python deps and pre-commit hooks.
- `make ingest`: Download Kaggle dataset → `data/raw/<timestamp>` (requires `.env` + Kaggle CLI).
- `make parquet`: Convert latest raw CSVs → Parquet in `data/parquet/<timestamp>`.
- `make warehouse`: Load Parquet into DuckDB at `warehouse/transfermarkt.duckdb`.
- `make dbt`: Run dbt models and schema tests using the `transform/` profile.
- `make dq`: Placeholder for Great Expectations checkpoints.
- `make app`: Launch Streamlit locally.
- `make run`: End-to-end: ingest → parquet → warehouse → dbt → dq → app.
Example: `cp .env.example .env && make setup && make ingest`.

## Coding Style & Naming Conventions
- Python 3.12. Format with Black (88 cols) and lint with Ruff (pre-commit configured).
- Use snake_case for modules, functions, and variables; keep scripts single-purpose.
- dbt: stage models prefixed `stg_` under `transform/models/stg/`; macros in `transform/macros/`.

## Testing Guidelines
- dbt tests: define in `transform/models/**/schema.yml`; run via `make dbt`.
- Data quality: integrate Great Expectations, then execute with `make dq` (stub present).
- Python scripts are runnable directly for sanity checks, e.g., `python ingest/csv_to_parquet.py SRC DST`.

## Commit & Pull Request Guidelines
- Commits: short, imperative tense (e.g., "Initialize dbt", "Add DuckDB loader").
- PRs: include purpose, key changes, linked issues, and verification notes (row counts, sample queries, Streamlit screenshots). Mention impacted `make` targets and `.env` changes.
- Before opening a PR: run `pre-commit run -a` and `make dbt`.

## Security & Configuration Tips
- Copy `.env.example` to `.env`; set `DATA_DIR`, `RAW_DIR`, `PARQUET_DIR`, `DUCKDB_PATH`, `KAGGLE_DATASET`.
- Configure Kaggle CLI (`~/.kaggle/kaggle.json`) before `make ingest`.
- Never commit secrets; `.env` is gitignored.
