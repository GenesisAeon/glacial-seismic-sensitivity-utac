"""v0.3 S0: freeze the case list -> results/v03/s0_case_list.json (+ SHA-256 printed).

Usage: python scripts/v03_freeze_s0.py   (refuses to overwrite a different frozen file)
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import UTC, datetime

from glacial_seismic_sensitivity_utac import config as C
from glacial_seismic_sensitivity_utac import v03_cases

OUT = C.OUT / "v03" / "s0_case_list.json"


def main() -> int:
    payload = json.loads(json.dumps(v03_cases.s0_payload()))  # tuples -> lists
    if OUT.exists():
        old = json.loads(OUT.read_text(encoding="utf-8"))
        frozen_at = old.pop("frozen_utc", None)
        if old != payload:
            print("S0 case list already frozen and differs -> amendment required", file=sys.stderr)
            return 1
        payload["frozen_utc"] = frozen_at
    else:
        payload["frozen_utc"] = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    OUT.write_text(text, encoding="utf-8")
    print(OUT, hashlib.sha256(text.encode("utf-8")).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
