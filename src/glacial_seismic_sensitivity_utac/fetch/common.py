"""Shared HTTP helper and the unified catalogue schema."""

from __future__ import annotations

import time

import requests

UNIFIED_COLUMNS = ["time", "latitude", "longitude", "depth", "mag", "magType", "id", "etype"]
USER_AGENT = "glacial-seismic-sensitivity-utac (GenesisAeon P133; research use)"


def http_get(
    url: str,
    params: dict[str, object] | None = None,
    timeout: tuple[float, float] = (30.0, 300.0),
    retries: int = 5,
    ok_empty: tuple[int, ...] = (204,),
) -> str:
    """GET with retries. Returns '' for 'no data' status codes (e.g. FDSN 204)."""
    last = ""
    for i in range(retries):
        try:
            r = requests.get(
                url,
                params=params,  # type: ignore[arg-type]
                timeout=timeout,
                headers={"User-Agent": USER_AGENT},
            )
            if r.status_code == 200:
                return r.text
            if r.status_code in ok_empty:
                return ""
            last = f"HTTP {r.status_code}: {r.text[:200]}"
            if r.status_code == 400 and "exceed" in r.text.lower():
                raise ValueError("too many events in one request")
        except requests.RequestException as exc:  # pragma: no cover - network
            last = str(exc)
        time.sleep(5 * (i + 1))
    raise RuntimeError(f"download failed: {url} {params} ({last})")
