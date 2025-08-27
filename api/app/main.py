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


@app.get("/health")
def health():
    return {"ok": True}
