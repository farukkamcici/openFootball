# Repository Guidelines

## Project Structure & Module Organization
- `ingest/`: Python scripts for raw-to-parquet conversion (`csv_to_parquet.py`).
- `warehouse/`: DuckDB loader and DB artifacts (`load_duckdb.py`, `warehouse/*.duckdb`).
- `transform/`: dbt project (`dbt_project.yml`, `models/`, `macros/`, `target/`).
- `app/`: Streamlit app entrypoint (`make app` expects `app/Home.py`).
- `data/`: Local raw and parquet data managed via `.env` (`RAW_DIR`, `PARQUET_DIR`, `DATA_DIR`).
- `quality/`, `docs/`, `ops/`: Reserved for QA, docs, and ops glue.

## Build, Test, and Development Commands
- `make setup`: Install Python deps and pre-commit hooks.
- `make ingest`: Download Kaggle dataset to `data/raw/<timestamp>` (requires `.env`).
- `make parquet`: Convert latest raw CSVs → Parquet under `data/parquet/<timestamp>`.
- `make warehouse`: Load Parquet into DuckDB at `warehouse/transfermarkt.duckdb`.
- `make dbt`: Run dbt models and tests using the `transform/` profile.
- `make dq`: Placeholder for Great Expectations checkpoints.
- `make app`: Launch Streamlit app.
- `make run`: End-to-end: ingest → parquet → warehouse → dbt → dq → app.
Example: `cp .env.example .env && make setup && make ingest`.

## Coding Style & Naming Conventions
- Python 3.12. Format with Black (88 cols) and lint with Ruff (pre-commit configured).
- Use snake_case for modules, functions, and variables. Keep scripts single-purpose.
- dbt: stage models prefixed `stg_` under `transform/models/stg/`; macros live in `transform/macros/`.

## Testing Guidelines
- dbt schema tests defined in `transform/models/**/schema.yml`; run with `make dbt`.
- Data quality: integrate GE suites and checkpoints, then invoke via `make dq`.
- Python: keep logic testable; run scripts directly, e.g. `python ingest/csv_to_parquet.py SRC DST`.

## Commit & Pull Request Guidelines
- Commits: short, imperative tense (e.g., "Initialize dbt", "Add DuckDB loader").
- PRs: include purpose, key changes, linked issues, and verification notes (e.g., row counts, sample queries, Streamlit screenshots). Mention impacted Make targets and `.env` changes.
- Local checks before PR: `pre-commit run -a` and `make dbt`.

## Security & Configuration Tips
- Copy `.env.example` to `.env` and set `DATA_DIR`, `RAW_DIR`, `PARQUET_DIR`, `DUCKDB_PATH`, `KAGGLE_DATASET`.
- Configure Kaggle CLI (`~/.kaggle/kaggle.json`) before `make ingest`.
- Never commit secrets; `.env` is gitignored.
