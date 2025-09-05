import os
import pathlib
from contextlib import asynccontextmanager

import duckdb
from fastapi import FastAPI
from .routers import (
    meta,
    league,
    clubs,
    players,
    market,
    formations,
    managers,
    transfers,
    search,
    compare,
    analytics,
    system,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Open a minimal DuckDB connection to verify readiness before serving.

    Fail fast with a helpful error if the DB file is missing or not readable.
    """
    env = os.getenv("ENV", "dev").lower()
    if env == "prod":
        db_path = os.getenv("PROD_DB_PATH")
    else:
        db_path = os.getenv("DEV_DB_PATH")
    path = pathlib.Path(db_path)
    if not path.exists():
        raise RuntimeError(
            f"DuckDB file not found at {path}. Did you run api.startup_db?"
        )
    try:
        with duckdb.connect(str(path), read_only=True) as con:
            con.execute("SELECT 1").fetchone()
    except Exception as exc:
        raise RuntimeError(
            f"Failed to open DuckDB at {path} in read-only mode: {exc}"
        ) from exc
    yield


def get_conn() -> duckdb.DuckDBPyConnection:
    """Return a read-only DuckDB connection using ENV-based path keys.

    - ENV=dev → DEV_DB_PATH (default: warehouse/transfermarkt_serving.duckdb)
    - ENV=prod → PROD_DB_PATH (default: /tmp/transfermarkt_serving.duckdb)
    """
    env = os.getenv("ENV", "dev").lower()
    if env == "prod":
        db_path = os.getenv("PROD_DB_PATH")
    else:
        db_path = os.getenv("DEV_DB_PATH")
    return duckdb.connect(db_path, read_only=True)


app = FastAPI(title="OpenFootball API", lifespan=lifespan)

app.include_router(meta.router, prefix="/api", tags=["meta"])
app.include_router(league.router, prefix="/api", tags=["league"])
app.include_router(clubs.router, prefix="/api", tags=["clubs"])
app.include_router(players.router, prefix="/api", tags=["players"])
app.include_router(market.router, prefix="/api", tags=["market"])
app.include_router(formations.router, prefix="/api", tags=["formations"])
app.include_router(managers.router, prefix="/api", tags=["managers"])
app.include_router(transfers.router, prefix="/api", tags=["transfers"])
app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(compare.router, prefix="/api", tags=["compare"])
app.include_router(analytics.router, prefix="/api", tags=["analytics"])
app.include_router(system.router, prefix="/api", tags=["system"])


@app.get("/health")
def health():
    """Basic health endpoint."""
    return {"status": "ok"}
