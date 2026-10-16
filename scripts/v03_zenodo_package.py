"""Build (locally, NO upload) the Zenodo raw-data package for v0.3.

Verifies every file in data/raw/v03/ against results/v03/MANIFEST_v03.sha256, then writes
  <out>/gss-utac-v03-raw-snapshots.tar.gz   (deterministic: sorted, mtime 0, uid/gid 0)
  <out>/gss-utac-v03-raw-snapshots.tar.gz.sha256
  <out>/MANIFEST_v03.sha256, <out>/s1_snapshots.json (provenance: URL, time, SHA-256 per file)
Default <out>: ../zenodo_v03_package (outside the repository). Uploading is a manual step.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import shutil
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "v03"
MAN = ROOT / "results" / "v03" / "MANIFEST_v03.sha256"
NAME = "gss-utac-v03-raw-snapshots.tar.gz"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=ROOT.parent / "zenodo_v03_package")
    a = ap.parse_args()
    entries = [ln.split(None, 1) for ln in MAN.read_text().splitlines() if ln.strip()]
    bad = [n for h, n in entries if not (RAW / n.strip()).is_file() or sha(RAW / n.strip()) != h]
    if bad:
        print(f"{len(bad)} files missing/mismatched, e.g. {bad[:3]}", file=sys.stderr)
        return 1
    a.out.mkdir(parents=True, exist_ok=True)
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w", format=tarfile.PAX_FORMAT) as tar:
        for _, n in sorted(entries, key=lambda e: e[1]):
            n = n.strip()
            data = (RAW / n).read_bytes()
            ti = tarfile.TarInfo(f"v03_raw/{n}")
            ti.size, ti.mtime, ti.mode = len(data), 0, 0o644
            tar.addfile(ti, io.BytesIO(data))
    out = a.out / NAME
    with open(out, "wb") as f, gzip.GzipFile(fileobj=f, mode="wb", mtime=0, filename="") as gz:
        gz.write(buf.getvalue())
    (a.out / f"{NAME}.sha256").write_text(f"{sha(out)}  {NAME}\n")
    shutil.copy2(MAN, a.out / MAN.name)
    shutil.copy2(ROOT / "results" / "v03" / "s1_snapshots.json", a.out / "s1_snapshots.json")
    print(out, out.stat().st_size, sha(out), f"{len(entries)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
