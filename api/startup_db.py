"""Startup utility to ensure a local DuckDB copy from GitHub Releases.

This module downloads the release asset if missing, verifies its SHA256 using the
companion .sha256 file, and then atomically moves the file into place. Designed for
read-only serving in ephemeral containers (e.g., Railway free tier).

Env vars:
- ENV: "dev" or "prod" (selects which path key to use)
- DEV_DB_PATH: local destination path for dev (default: warehouse/transfermarkt_serving.duckdb)
- PROD_DB_PATH: local destination path for prod (default: /tmp/transfermarkt_serving.duckdb)
- RELEASE_DB_URL: HTTPS URL to the .duckdb asset (required)
- RELEASE_DB_SHA256: HTTPS URL to the .sha256 file (required)

Only prints a single success line on completion for clean logs.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Iterator

import requests


def sha256sum(path: Path) -> str:
    """Return the hex SHA256 of a file.

    Reading in chunks avoids loading the entire file into memory.
    """
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):  # 1MB chunks
            h.update(chunk)
    return h.hexdigest()


def _iter_chunks(resp: requests.Response, size: int = 1024 * 1024) -> Iterator[bytes]:
    """Yield response body in fixed-size chunks, skipping keep-alives."""
    for chunk in resp.iter_content(chunk_size=size):
        if chunk:  # filter out keep-alive chunks
            yield chunk


def stream_download(url: str, out: Path) -> None:
    """Stream download the URL to path `out` in 1MB chunks.

    Using streaming avoids high memory usage on cold starts.
    """
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with out.open("wb") as f:
            for chunk in _iter_chunks(r, size=1024 * 1024):
                f.write(chunk)


def ensure_db(local_path: str, asset_url: str, sha_url: str) -> str:
    """Ensure the DuckDB file exists at `local_path`, downloading and verifying if needed.

    Steps:
    - If the target exists, return immediately (idempotent).
    - Download to a temporary `.part` file.
    - Fetch SHA256 from `sha_url`, compare with the actual checksum.
    - On mismatch, delete the partial file and raise RuntimeError (fail loud).
    - On match, atomically move the file into place.
    """
    target = Path(local_path)
    if target.exists():
        return str(target)

    target.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = target.with_suffix(target.suffix + ".part")

    # Download the asset to a temporary path first to avoid partial files on failure.
    stream_download(asset_url, tmp_path)

    # Fetch the expected SHA256 and parse the first token (common format: "<sha>  <file>").
    resp = requests.get(sha_url, timeout=30)
    resp.raise_for_status()
    expected = resp.text.strip().split()[0].lower()

    actual = sha256sum(tmp_path)
    if actual.lower() != expected:
        try:
            tmp_path.unlink(missing_ok=True)
        finally:
            raise RuntimeError(
                "Checksum mismatch: expected SHA256 {} but got {}".format(
                    expected, actual
                )
            )

    # Atomic move avoids readers observing partial state.
    tmp_path.replace(target)
    return str(target)


def _main() -> None:
    # Resolve destination path strictly by ENV for consistency across services.
    env = os.getenv("ENV", "dev").lower()
    if env == "prod":
        local = os.getenv("PROD_DB_PATH", "/tmp/transfermarkt_serving.duckdb")
    else:
        local = os.getenv("DEV_DB_PATH", "warehouse/transfermarkt_serving.duckdb")
    asset = os.getenv("RELEASE_DB_URL")
    sha = os.getenv("RELEASE_DB_SHA256")

    if not asset or not sha:
        raise SystemExit(
            "RELEASE_DB_URL and RELEASE_DB_SHA256 must be set in environment."
        )

    path = ensure_db(local, asset, sha)
    print(f"DB ready at {path}")


if __name__ == "__main__":
    _main()
