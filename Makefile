SHELL := /bin/bash
TS := $(shell date +%Y%m%d_%H%M%S)

.PHONY: setup ingest parquet warehouse dbt dq app run help api startup-db smoke

help:
	@echo "Targets: setup | ingest | parquet | warehouse | dbt | dq | app | run"

setup:
	@set -a; [ -f .env ] && . ./.env || true; set +a; \
	echo ">> Install Python deps"; \
	python -m pip install -r requirements.txt || pip install -r requirements.txt; \
	echo ">> Install pre-commit hooks"; \
	pre-commit install || true

ingest:
	@set -a; [ -f .env ] && . ./.env || (echo "Missing .env"; exit 1); set +a; \
	[ -n "$$RAW_DIR" ] || (echo "RAW_DIR not set in .env"; exit 1); \
	[ -n "$$KAGGLE_DATASET" ] || (echo "KAGGLE_DATASET not set in .env"; exit 1); \
	out="$$RAW_DIR/$(TS)"; mkdir -p "$$out"; \
	echo ">> Downloading $$KAGGLE_DATASET to $$out"; \
	kaggle datasets download -d "$$KAGGLE_DATASET" -p "$$out" -o; \
	echo ">> Unzipping"; \
	unzip -q "$$out"/*.zip -d "$$out" || true; rm -f "$$out"/*.zip || true; \
	count=$$(find "$$out" -maxdepth 1 -type f -name "*.csv" | wc -l | tr -d ' '); \
	echo ">> CSV files: $$count"; \
	mkdir -p "$$DATA_DIR"; echo "$(TS)" > "$$DATA_DIR/LATEST"; \
	echo ">> Wrote $$DATA_DIR/LATEST with timestamp $(TS)"

parquet:
	@set -a; [ -f .env ] && . ./.env || (echo "Missing .env"; exit 1); set +a; \
	[ -f "$$DATA_DIR/LATEST" ] || (echo "Run 'make ingest' first (no LATEST)"; exit 1); \
	TS_CUR=$$(cat "$$DATA_DIR/LATEST"); \
	SRC="$$RAW_DIR/$$TS_CUR"; \
	DST="$$PARQUET_DIR/$$TS_CUR"; \
	mkdir -p "$$DST"; \
	echo ">> Converting CSV -> Parquet from $$SRC to $$DST"; \
	python ingest/csv_to_parquet.py "$$SRC" "$$DST"


warehouse:
	@set -a; [ -f .env ] && . ./.env || (echo "Missing .env"; exit 1); set +a; \
	TS_CUR=$$(cat "$$DATA_DIR/LATEST"); \
	PQ_DIR="$$PARQUET_DIR/$$TS_CUR"; \
	[ -d "$$PQ_DIR" ] || (echo "Run 'make parquet' first"; exit 1); \
	mkdir -p "$$(dirname "$$DUCKDB_PATH")"; \
	echo ">> Loading $$PQ_DIR into $$DUCKDB_PATH"; \
	python warehouse/load_duckdb.py "$$DUCKDB_PATH" "$$PQ_DIR"


dbt:
	@set -a; [ -f .env ] && . ./.env || true; set +a; \
	if [ -d transform ]; then \
	  echo ">> dbt run/test"; \
	  dbt run --profiles-dir transform || true; \
	  dbt test --profiles-dir transform || true; \
	else \
	  echo ">> Skipping dbt (transform/ not found)"; \
	fi

dq:
	@echo ">> GE placeholder (define suites, then run checkpoint)"; \
	echo "   e.g., great_expectations --v3-api checkpoint run my_checkpoint" || true

app:
	@set -a; [ -f .env ] && . ./.env || true; set +a; \
	echo ">> Starting Streamlit"; \
	streamlit run app/Home.py

run: ingest parquet warehouse dbt dq app
	@echo ">> Done."

# --- API dev utilities ---

api:
	@set -a; [ -f .env ] && . ./.env || true; set +a; \
	echo ">> Starting FastAPI (uvicorn)"; \
	uvicorn api.app.main:app --reload

startup-db:
	@set -a; [ -f .env ] && . ./.env || true; set +a; \
	echo ">> Ensuring local DuckDB from release"; \
	python -m api.startup_db

smoke:
	@URL=$${OPENFOOTBALL_API_BASE:-http://127.0.0.1:8000}; \
	echo ">> Smoke: health"; curl -sS "$$URL/api/health" || true; echo; \
	echo ">> Smoke: seasons"; curl -sS "$$URL/api/seasons" || true; echo; \
	echo ">> Smoke: version"; curl -sS "$$URL/api/version" || true; echo
