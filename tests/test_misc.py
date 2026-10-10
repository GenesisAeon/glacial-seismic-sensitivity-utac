from __future__ import annotations

import inspect
import json
import re

import numpy as np
import pandas as pd

from glacial_seismic_sensitivity_utac import config as C
from glacial_seismic_sensitivity_utac import constants, honesty
from glacial_seismic_sensitivity_utac.cli import main
from glacial_seismic_sensitivity_utac.fetch import catalogs
from glacial_seismic_sensitivity_utac.seasonal import schuster_full
from glacial_seismic_sensitivity_utac.stats_tests import bh, block_perm_test, group_perm, iaaft

from .conftest import FIXTURES


def test_honesty_all_false():
    fns = [f for _, f in inspect.getmembers(honesty, inspect.isfunction)]
    assert len(fns) >= 5
    assert all(f() is False for f in fns)


def test_constants_dois():
    assert constants.PACKAGE_ID == 133 and not constants.PACKAGE_ID_PROVISIONAL
    assert constants.REGISTRY_CLASS == "KLIMA-KRYO-13"
    for c in constants.ALL_CITATIONS.values():
        assert re.match(r"^10\.\d{4,9}/\S+$", c["doi"])


def test_bh_and_perm():
    q, s = bh(np.array([0.001, 0.01, 0.04, 0.5]))
    assert s[0] and s[1] and not s[3]
    assert np.all(np.diff(q[np.argsort([0.001, 0.01, 0.04, 0.5])]) >= -1e-12)
    rng = np.random.default_rng(0)
    tau, p = block_perm_test(np.arange(20, dtype=float), rng, n=200)
    assert tau > 0.9 and p < 0.05
    d, pv, n = group_perm(
        {"a": 1, "b": 1.1, "c": 0, "d": 0.1}, {"a": True, "b": True, "c": False, "d": False}
    )
    assert d > 0.9 and n == 4 and abs(pv - 2 / 6) < 1e-9


def test_iaaft_preserves_distribution():
    rng = np.random.default_rng(1)
    x = rng.poisson(5, 240).astype(float)
    y = iaaft(x, rng)
    assert np.allclose(np.sort(x), np.sort(y))


def test_schuster():
    t = np.random.default_rng(2).uniform(0, 30, 3000)
    assert schuster_full(t)["p"] > 0.001
    t2 = np.concatenate([t, np.arange(30) + 0.85])
    assert schuster_full(np.tile(t2[-30:], 30))["amp"] > 0.9


def test_fdsn_text_parser():
    df = catalogs._fdsn_text((FIXTURES / "fdsn_text_sample.txt").read_text(encoding="utf-8"))
    assert len(df) == 3 and list(df.columns) == catalogs.UNIFIED_COLUMNS
    assert df.etype.str.contains("earthquake").sum() == 2


def test_geus_parser(monkeypatch):
    monkeypatch.setattr(
        catalogs,
        "http_get",
        lambda *a, **k: (FIXTURES / "geus_sample.json").read_text(encoding="utf-8"),
    )
    df = catalogs.fetch_geus(C.REGIONS["Greenland_GEUS"])
    assert list(df.id) == ["g1", "g2"]  # g3 before 1990, g4 explosion
    assert (
        json.loads((FIXTURES / "geus_sample.json").read_text(encoding="utf-8"))["type"]
        == "FeatureCollection"
    )


def test_cli_info_and_lag(capsys):
    assert main(["info"]) == 0
    assert main(["lag"]) == 0
    out = capsys.readouterr().out
    assert "SE_Alaska_AK" in out and "tau_yr" in out


def test_regions_consistent():
    for n, r in C.REGIONS.items():
        a, b, c, d = r.box
        assert a < b and c < d, n
        assert r.group in ("mountain", "icesheet", "control")
    assert isinstance(pd.Timestamp(C.CONFIRMATORY_START), pd.Timestamp)


def test_confirmatory_on_synthetic_future(make_catalog):
    from glacial_seismic_sensitivity_utac import confirmatory
    from glacial_seismic_sensitivity_utac.catalog import prepare

    df = prepare(make_catalog(n_years=40, rate=600, b0=0.4, seed=9))  # 1990-2029
    params = dict(
        confirmatory_data_start="2026-11-01",
        looks={"look1_2029-10-31": dict(years=3, alpha=0.01)},
        regions={
            "X": dict(mc=2.0, log_eta0=-99.0, phase_peak_month=11.0, b_ref=0.0, b_ref_se=0.02)
        },
    )
    r = confirmatory.confirmatory_test("X", "2029-10-31", params, df)
    assert r["n_new_events"] > 1000
    assert r["reject_H0"] == "True"
    assert abs(float(r["b_new"]) - 0.4) < 0.1
