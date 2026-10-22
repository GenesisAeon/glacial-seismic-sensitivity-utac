"""AP8: the bounds table in docs/adequacy/BOUNDS.md is regenerated deterministically."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]


def _mod() -> ModuleType:
    spec = importlib.util.spec_from_file_location("ap8", ROOT / "scripts" / "ap8_bounds_table.py")
    assert spec is not None and spec.loader is not None
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_bounds_table_matches_doc_and_flags_p() -> None:
    m = _mod()
    t = m.table()
    assert t == m.table()
    doc = m.DOC.read_text(encoding="utf-8")
    assert f"{m.BEGIN}\n{t}{m.END}" in doc
    p_rows = [r for r in t.splitlines() if "| p |" in r]
    assert len(p_rows) == 8
    assert sum("**AT**" in r for r in p_rows) == 7
