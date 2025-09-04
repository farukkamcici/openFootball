import os
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def api_health():
    """Health probe for API service."""
    return {"status": "ok"}


@router.get("/version")
def version():
    """Return build/version metadata if available."""
    git_sha = os.getenv("GIT_SHA") or os.getenv("COMMIT_SHA")
    build_time = os.getenv("BUILD_TIME")
    return {
        "version": git_sha or "dev",
        "build_time": build_time or None,
    }


@router.get("/limits")
def limits():
    """Return API default limits and thresholds."""
    return {
        "value_perf_default_limit": 500,
        "efficiency_screener_default_limit": 100,
    }
