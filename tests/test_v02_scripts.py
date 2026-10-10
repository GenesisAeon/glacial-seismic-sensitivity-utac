"""Calibration/recovery scripts must use the production geometry of v02 (review B1: Codex and
Claude Code found the H2.2 windows shifted by one year in the calibration that underlies the
frozen SE factor)."""

from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
from types import ModuleType

from glacial_seismic_sensitivity_utac import v02

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_calibration_uses_production_geometry() -> None:
    g = _load("v02_calibration_study").geometry()
    assert g == dict(
        t_sim0=v02.FIT_T0 - v02.HISTORY_YEARS,
        t0=v02.FIT_T0,
        t1=v02.FIT_T1,
        tmax=v02.TMAX,
        win_a=v02.WIN_A,
        win_b=v02.WIN_B,
    )
    # production windows are half-open calendar years 2008-2019 and 2020-2025
    assert v02.WIN_A == (2008.0, 2020.0) and v02.WIN_B == (2020.0, 2026.0)
    assert (v02.FIT_T0, v02.FIT_T1) == (1995.0, 2026.0)


def _literal_tuples(src: str) -> set[tuple[object, ...]]:
    out = set()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Tuple) and all(
            isinstance(e, ast.Constant) and isinstance(e.value, (int, float)) for e in node.elts
        ):
            out.add(tuple(float(e.value) for e in node.elts if isinstance(e, ast.Constant)))
    return out


def test_no_literal_window_tuples_in_scripts() -> None:
    # windows must come from v02 (single source of truth); docstrings may mention the history
    for f in (ROOT / "scripts").glob("v02_*.py"):
        lits = _literal_tuples(f.read_text(encoding="utf-8"))
        for w in [(2008.0, 2019.0), (2020.0, 2025.0), v02.WIN_A, v02.WIN_B]:
            assert w not in lits, (f.name, w)
        calls = [
            n
            for n in ast.walk(ast.parse(f.read_text(encoding="utf-8")))
            if isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "linspace"
        ]
        for c in calls:  # true window means must not be computed on hard-coded windows either
            nums = [a.value for a in c.args[:2] if isinstance(a, ast.Constant)]
            assert nums not in ([2008, 2019], [2020, 2025]), f.name
    rec = (ROOT / "scripts" / "v02_recovery_study.py").read_text(encoding="utf-8")
    assert "WIN_A" in rec and "WIN_B" in rec
