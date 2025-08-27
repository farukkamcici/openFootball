import os
import pathlib
import time
import duckdb
import boto3
from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv("ENV", "dev")
BASE_DIR = pathlib.Path(__file__).resolve().parents[2]
LOCAL_DB = os.getenv("LOCAL_DB_PATH", "warehouse/transfermarkt.duckdb")
S3_URI = os.getenv("WAREHOUSE_S3_URI")
CACHE_PATH = pathlib.Path(os.getenv("LOCAL_DB_CACHE", "/data/transfermarkt.duckdb"))
REFRESH_SEC = int(os.getenv("REFRESH_SEC", "0"))


def ensure_db_local() -> str:
    """Return path to DB. If prod → download and cache."""
    if ENV == "dev":
        return LOCAL_DB

    if not CACHE_PATH.exists() or (
        REFRESH_SEC and (time.time() - CACHE_PATH.stat().st_mtime) > REFRESH_SEC
    ):
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        s3 = boto3.client("s3")
        bucket, key = S3_URI.replace("s3://", "", 1).split("/", 1)
        s3.download_file(bucket, key, str(CACHE_PATH))
    return str(CACHE_PATH)


def get_conn() -> duckdb.DuckDBPyConnection:
    """Return DuckDB read-only connection."""
    db_path = str((BASE_DIR / LOCAL_DB).resolve())
    return duckdb.connect(db_path, read_only=True)
