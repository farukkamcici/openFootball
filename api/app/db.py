import os
import pathlib
import duckdb

ENV = os.getenv("ENV", "dev").lower()
BASE_DIR = pathlib.Path(__file__).resolve().parents[2]
_DEFAULT_DEV = "warehouse/transfermarkt_serving.duckdb"
_DEFAULT_PROD = "/tmp/transfermarkt_serving.duckdb"
LOCAL_DB = (
    os.getenv("PROD_DB_PATH", _DEFAULT_PROD)
    if ENV == "prod"
    else os.getenv("DEV_DB_PATH", _DEFAULT_DEV)
)


def get_conn() -> duckdb.DuckDBPyConnection:
    """Return DuckDB read-only connection."""
    db_path = LOCAL_DB
    # If dev and path is relative, resolve under repo root for convenience.
    if not pathlib.Path(db_path).is_absolute():
        db_path = str((BASE_DIR / db_path).resolve())
    return duckdb.connect(db_path, read_only=True)
