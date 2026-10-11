"""Driver registry (v0.3): schema and validation for ``drivers/registry.yaml``.

The registry is bookkeeping: it lists every candidate driver that has come up (literature,
own research, AI-generated reports) together with its evidence level and pre-registration
status, so that new ideas cannot slip into analyses unnoticed.

Rules (docs/PLAN_v0.3_KOLLAPS_MODUL_ENTWURF.md, section 3):
  1. every entry has >= 1 DOI, and every DOI is listed in ``drivers/verified_dois.tsv``
     (resolved via Crossref/DataCite);
  2. ``status: active`` requires a frozen pre-registration (``prereg: frozen:...``);
  3. ``status: rejected`` entries stay in the file and carry a reason in ``notes``;
  4. entries originating from AI-generated reports (``origin: ai_report``) may only be
     ``status: candidate`` with ``evidence: speculative``.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any

import yaml

from . import config as C

REGISTRY = C.ROOT / "drivers" / "registry.yaml"
VERIFIED = C.ROOT / "drivers" / "verified_dois.tsv"

REQUIRED = (
    "id",
    "name",
    "mechanism",
    "evidence",
    "origin",
    "sources",
    "observables",
    "data",
    "status",
    "introduced_in",
    "prereg",
    "notes",
)
EVIDENCE = ("established", "reported", "speculative")
STATUS = ("candidate", "active", "rejected")
ORIGIN = ("literature", "own_research", "ai_report")
PREREG_RE = re.compile(r"^(none|exploratory|prospective|frozen:.+)$")
ID_RE = re.compile(r"^D-[A-Z0-9]+$")
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")
VERSION_RE = re.compile(r"^v\d+\.\d+(\.\d+)?(-dev)?$")


def load(path: Path = REGISTRY) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("registry root must be a mapping")
    return data


def verified_dois(path: Path = VERIFIED) -> set[str]:
    with path.open(encoding="utf-8") as fh:
        return {row["doi"].strip().lower() for row in csv.DictReader(fh, delimiter="\t")}


def validate(data: dict[str, Any], verified: set[str] | None = None) -> list[str]:
    """Return a list of human-readable rule violations (empty = valid)."""
    errs: list[str] = []
    if data.get("schema_version") != 1:
        errs.append("schema_version must be 1")
    entries = data.get("drivers")
    if not isinstance(entries, list) or not entries:
        return errs + ["'drivers' must be a non-empty list"]
    seen: set[str] = set()
    for i, e in enumerate(entries):
        tag = f"entry {i} ({e.get('id', '?') if isinstance(e, dict) else '?'})"
        if not isinstance(e, dict):
            errs.append(f"{tag}: not a mapping")
            continue
        missing = [k for k in REQUIRED if k not in e]
        extra = [k for k in e if k not in REQUIRED]
        if missing:
            errs.append(f"{tag}: missing {missing}")
            continue
        if extra:
            errs.append(f"{tag}: unknown keys {extra}")
        if not isinstance(e["id"], str) or not ID_RE.match(e["id"]):
            errs.append(f"{tag}: bad id")
        elif e["id"] in seen:
            errs.append(f"{tag}: duplicate id")
        else:
            seen.add(e["id"])
        for k in ("name", "mechanism"):
            if not isinstance(e[k], str) or not e[k].strip():
                errs.append(f"{tag}: '{k}' must be a non-empty string")
        if e["evidence"] not in EVIDENCE:
            errs.append(f"{tag}: evidence must be one of {EVIDENCE}")
        if e["status"] not in STATUS:
            errs.append(f"{tag}: status must be one of {STATUS}")
        if e["origin"] not in ORIGIN:
            errs.append(f"{tag}: origin must be one of {ORIGIN}")
        if not isinstance(e["prereg"], str) or not PREREG_RE.match(e["prereg"]):
            errs.append(f"{tag}: prereg must be none|exploratory|prospective|frozen:<ref>")
        if not isinstance(e["introduced_in"], str) or not VERSION_RE.match(e["introduced_in"]):
            errs.append(f"{tag}: introduced_in must look like v0.3-dev or v0.2.0")
        for k in ("observables", "data"):
            if not isinstance(e[k], list):
                errs.append(f"{tag}: '{k}' must be a list")
        src = e["sources"]
        if not isinstance(src, list) or not src:
            errs.append(f"{tag}: rule 1 - at least one DOI required")
        else:
            for d in src:
                if not isinstance(d, str) or not DOI_RE.match(d):
                    errs.append(f"{tag}: '{d}' is not a DOI")
                elif verified is not None and d.lower() not in verified:
                    errs.append(f"{tag}: rule 1 - DOI {d} not in verified_dois.tsv")
        if e["status"] == "active" and not str(e["prereg"]).startswith("frozen:"):
            errs.append(f"{tag}: rule 2 - active requires prereg frozen:<ref>")
        if e["status"] == "rejected" and not str(e["notes"] or "").strip():
            errs.append(f"{tag}: rule 3 - rejected entries need a reason in notes")
        if e["origin"] == "ai_report" and (
            e["status"] != "candidate" or e["evidence"] != "speculative"
        ):
            errs.append(f"{tag}: rule 4 - ai_report entries must be candidate + speculative")
    return errs


def check(path: Path = REGISTRY, verified_path: Path = VERIFIED) -> list[str]:
    return validate(load(path), verified_dois(verified_path))
