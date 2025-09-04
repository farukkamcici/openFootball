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

app = FastAPI(title="OpenFootball API")

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
