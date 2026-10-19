"""AP0: guard tests for the read-only adequacy module (no frozen file may change)."""

from __future__ import annotations

import ast
import dataclasses
import shutil
from pathlib import Path

import numpy as np
import pytest

from glacial_seismic_sensitivity_utac import etas_adequacy, etas_nonstat
from glacial_seismic_sensitivity_utac.etas_adequacy import frozen

from .adequacy_frozen_inventory import ROOT, file_matches, frozen_inventory

PKG = ROOT / "src" / "glacial_seismic_sensitivity_utac" / "etas_adequacy"


def test_inventory_covers_all_frozen_lists() -> None:
    inv = frozen_inventory()
    assert "results/frozen_v02_baselines.json" in inv
    assert inv["results/frozen_v02_baselines.json"] == frozen.BASELINES_SHA256
    assert "src/glacial_seismic_sensitivity_utac/etas_nonstat.py" in inv
    assert "src/glacial_seismic_sensitivity_utac/v03_discriminator.py" in inv
    assert len(inv) >= 15


@pytest.mark.parametrize("rel", sorted(frozen_inventory()))
def test_frozen_file_unchanged(rel: str) -> None:
    assert file_matches(rel, frozen_inventory()[rel]), f"frozen file changed: {rel}"


def test_load_baselines_reads_all_regions_read_only() -> None:
    b = etas_adequacy.load_baselines()
    assert tuple(b) == frozen.REGIONS and len(b) == 8
    se = b["SE_Alaska_AK"]
    assert se.mc_ref == 2.1 and se.p == 1.0001 and se.tmax_yr == 1.0 and se.n_ref_years == 10
    assert abs(se.mu_ref - np.exp(4.046619702333692)) < 1e-12
    with pytest.raises(TypeError):
        b["SE_Alaska_AK"] = se  # type: ignore[index]
    with pytest.raises(dataclasses.FrozenInstanceError):
        se.p = 1.2  # type: ignore[misc]


def test_load_baselines_rejects_manipulated_copy(tmp_path: Path) -> None:
    src = frozen.BASELINES_PATH
    good = tmp_path / "good.json"
    shutil.copyfile(src, good)
    assert len(etas_adequacy.load_baselines(good)) == 8
    bad = tmp_path / "bad.json"
    data = src.read_bytes().replace(b'"p": 1.0001', b'"p": 1.0002', 1)
    assert data != src.read_bytes()
    bad.write_bytes(data)
    with pytest.raises(etas_adequacy.FrozenFileError, match="SHA-256"):
        etas_adequacy.load_baselines(bad)


def test_load_baselines_rejects_wrong_structure_even_with_matching_hash(tmp_path: Path) -> None:
    p = tmp_path / "x.json"
    p.write_text('{"regions": {"SE_Alaska_AK": {"p": 1.0}}}', encoding="utf-8")
    with pytest.raises(etas_adequacy.FrozenFileError, match="region set"):
        etas_adequacy.load_baselines(p, expected_sha256=frozen.sha256_bytes(p.read_bytes()))


def test_trig_is_compatible_with_frozen_mu_window_mle() -> None:
    se = etas_adequacy.load_baselines()["SE_Alaska_AK"]
    t = np.array([2026.10, 2026.30, 2026.31, 2026.70])
    m = np.array([2.1, 3.0, 2.2, 2.4])
    r = etas_nonstat.mu_window_mle(t, m, se.mc_ref, se.trig(), 2026.0, 2027.0)
    assert r["n"] == 4.0 and np.isfinite(r["log_mu"])


def _write_calls(tree: ast.AST) -> list[ast.Call]:
    calls = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")
        if name in {"write_text", "write_bytes", "unlink", "rename", "replace", "rmtree"}:
            calls.append(node)
        elif name == "open":
            modes = list(node.args[1:2]) + [k.value for k in node.keywords if k.arg == "mode"]
            for mode in modes:
                if isinstance(mode, ast.Constant) and set(str(mode.value)) & set("wax+"):
                    calls.append(node)
    return calls


def test_no_write_call_targets_a_frozen_path() -> None:
    """AST check: frozen.py writes nothing; no write call anywhere in the package mentions
    'frozen' or 'PREREGISTRATION' in its arguments."""
    files = sorted(PKG.glob("*.py"))
    assert files
    for f in files:
        src = f.read_text(encoding="utf-8")
        calls = _write_calls(ast.parse(src))
        if f.name == "frozen.py":
            assert not calls, "frozen.py must not write"
        for c in calls:
            seg = ast.get_source_segment(src, c) or ""
            assert "frozen" not in seg.lower() and "preregistration" not in seg.lower(), seg
