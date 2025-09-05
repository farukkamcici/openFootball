import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import get_conn
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
    """Open a DuckDB connection and run a trivial query to ensure readiness."""
    try:
        con = get_conn()
        try:
            con.execute("SELECT 1").fetchone()
        finally:
            con.close()
    except Exception as exc:
        raise RuntimeError(
            "Failed to open DuckDB with current ENV/paths. "
            "Ensure startup_db ran and ENV/DEV_DB_PATH/PROD_DB_PATH are set."
        ) from exc
    yield


app = FastAPI(title="OpenFootball API", lifespan=lifespan)

# Allow browser apps (e.g., Streamlit) to call the API from other origins
allow_origins = os.getenv("CORS_ALLOW_ORIGINS", "*")
origins = [o.strip() for o in allow_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

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
