"""Fetch everything (network). Usage: ``glacial-sensitivity fetch``."""

from __future__ import annotations

import traceback
from collections.abc import Callable

from .. import config as C
from .auxdata import fetch_cities, fetch_grace, fetch_precip
from .catalogs import fetch_region


def fetch_all(regions: list[str] | None = None, force: bool = False) -> dict[str, str]:
    status: dict[str, str] = {}
    jobs: list[tuple[str, Callable[[], object]]] = [
        ("cities", lambda: fetch_cities(force)),
        ("grace", lambda: fetch_grace(force)),
    ]
    for job, fn in jobs:
        try:
            fn()
            status[job] = "ok"
        except Exception as exc:  # pragma: no cover - network
            status[job] = f"FAILED: {exc}"
    for name in regions or list(C.REGIONS):
        try:
            df = fetch_region(name, force)
            status[name] = f"ok ({len(df)} events)"
        except Exception as exc:  # pragma: no cover - network
            traceback.print_exc()
            status[name] = f"FAILED: {exc}"
    for name in C.PRECIP_POINTS:
        if regions and name not in regions:
            continue
        try:
            fetch_precip(name, force)
            status[f"precip_{name}"] = "ok"
        except Exception as exc:  # pragma: no cover - network
            status[f"precip_{name}"] = f"FAILED: {exc}"
    for k, v in status.items():
        print(f"{k:32s} {v}", flush=True)
    return status
