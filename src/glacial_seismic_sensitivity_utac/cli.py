"""Command line interface: ``glacial-sensitivity {fetch,run,sensitivity,lag,plot,all,info}``."""

from __future__ import annotations

import argparse
import sys

from . import __version__
from . import config as C


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="glacial-sensitivity",
        description="Glacial unloading - seismic sensitivity tests (GenesisAeon)",
    )
    ap.add_argument("--version", action="version", version=__version__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch", help="download catalogues, GRACE, ERA5 precipitation, cities")
    f.add_argument("--regions", nargs="*")
    f.add_argument("--force", action="store_true")
    r = sub.add_parser("run", help="full analysis (sensitivity, lag, power, criticality)")
    r.add_argument("--regions", nargs="*")
    r.add_argument("--no-criticality", action="store_true")
    sub.add_parser("lag", help="print GIA relaxation-time table")
    sub.add_parser("plot", help="charts from existing results")
    a = sub.add_parser("all", help="fetch + run + plot")
    a.add_argument("--no-criticality", action="store_true")
    sub.add_parser("info", help="regions and paths")
    args = ap.parse_args(argv)

    if args.cmd == "fetch":
        from .fetch.run import fetch_all

        st = fetch_all(args.regions, args.force)
        return 0 if all(not v.startswith("FAILED") for v in st.values()) else 1
    if args.cmd == "run":
        from .pipeline import run_all

        run_all(args.regions, criticality_battery=not args.no_criticality)
        return 0
    if args.cmd == "lag":
        from .lagmodel import relaxation_table

        print(relaxation_table().round(3).to_string())
        return 0
    if args.cmd == "plot":
        from .plots import all_charts

        all_charts()
        return 0
    if args.cmd == "all":
        from .fetch.run import fetch_all
        from .pipeline import run_all
        from .plots import all_charts

        fetch_all()
        run_all(criticality_battery=not args.no_criticality)
        all_charts()
        return 0
    if args.cmd == "info":
        print(f"raw: {C.RAW}\nout: {C.OUT}\ncharts: {C.CHARTS}")
        for n, reg in C.REGIONS.items():
            print(f"{n:26s} {reg.group:9s} {reg.source:10s} M>={reg.minmag} box={reg.box}")
        return 0
    return 2  # pragma: no cover


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
