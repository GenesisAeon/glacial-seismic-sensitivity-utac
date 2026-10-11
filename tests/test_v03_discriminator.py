"""v0.3 S2: feature extraction and rule-based source discriminator (synthetic inputs)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from glacial_seismic_sensitivity_utac import v03_discriminator as D
from glacial_seismic_sensitivity_utac import v03_features as F

TH = D.Thresholds()


def _detail(mts: list[dict], origins: list[dict]) -> dict:
    return {
        "properties": {
            "products": {
                "moment-tensor": [{"properties": p} for p in mts],
                "origin": [{"properties": p} for p in origins],
            }
        }
    }


def test_mt_parsing_fraction_percent_and_iso() -> None:
    full = {
        "percent-double-couple": "0.06",
        "tensor-mrr": "-1.804E+15",
        "tensor-mtt": "-4.091E+14",
        "tensor-mpp": "-4.118E+14",
        "scalar-moment": "1.917E+15",
    }
    j = _detail([full], [{"magnitude-type": "ml", "magnitude": "3.93"}])
    assert F.mt_percent_dc(j) == pytest.approx(6.0)
    assert F.mt_iso_fraction(j) == pytest.approx(-2.6249e15 / 3 / 1.917e15, rel=1e-3)
    dev = {
        "percent-double-couple": "89.07",
        "tensor-mrr": "1",
        "tensor-mtt": "-0.5",
        "tensor-mpp": "-0.5",
        "scalar-moment": "1",
    }
    j2 = _detail([dev], [])
    assert F.mt_percent_dc(j2) == pytest.approx(89.07)  # stored as percent
    assert F.mt_iso_fraction(j2) == 0.0
    assert np.isnan(F.mt_iso_fraction(_detail([], [])))


def test_magnitudes_long_short() -> None:
    j = _detail(
        [{"derived-magnitude-type": "Mww", "derived-magnitude": "5.3"}],
        [{"magnitude-type": "mb", "magnitude": "5.0"}],
    )
    mags = F.magnitudes_from_detail(j)
    lo, sh, tlo, tsh = F.long_short(mags)
    assert (lo, sh, tlo, tsh) == (5.3, 5.0, "mww", "mb")


def test_sequence_features() -> None:
    t0 = pd.Timestamp("2020-01-01T12:00:00", tz="UTC")
    cat = pd.DataFrame(
        {
            "time": [
                t0 - pd.Timedelta(minutes=8),
                t0,
                t0 + pd.Timedelta(days=1),
                t0 + pd.Timedelta(days=40),
            ],
            "lat": [10.0, 10.0, 10.01, 10.0],
            "lon": [20.0, 20.0, 20.0, 20.0],
            "depth": [0.0, 0.0, 2.0, 2.0],
            "mag": [6.0, 4.0, 3.5, 4.6],
            "magtype": ["mb"] * 4,
            "type": ["nuclear explosion", "collapse", "earthquake", "earthquake"],
            "id": ["a", "b", "c", "d"],
        }
    )
    s = F.sequence_features(cat, t0, 10.0, 20.0, 4.0, exclude_id="b")
    assert s["preceded_by_larger_1h"] == 1.0
    assert s["trigger_type"] == "nuclear explosion"
    assert s["n_after_30d_ge_m_minus2"] == 1.0
    assert s["bath_dm"] == pytest.approx(0.5)
    assert s["n_m45_pm_half_year"] == 2.0  # a (6.0) and d (4.6)


def test_fdsn_text_loader(tmp_path: Path) -> None:
    p = tmp_path / "k.txt"
    p.write_text(
        "#EventID|Time|Latitude|Longitude|Depth/km|Author|Catalog|Contributor|ContributorID|"
        "MagType|Magnitude|MagAuthor|EventLocationName|EventType\n"
        "k1|2012-08-16T20:30:33.28|53.35|6.67|3.0|||KNMI|k1|MLn|3.6||Huizinge|"
        "induced or triggered event\n",
        encoding="utf-8",
    )
    d = F.load_fdsn_text(p)
    assert d.iloc[0].mag == 3.6 and d.iloc[0].type == "induced or triggered event"


@pytest.mark.parametrize(
    ("row", "mode", "expected"),
    [
        ({"catalog_type": "landslide", "depth_km": 0.0}, "full", ("mass_movement", "L0")),
        ({"catalog_type": "landslide", "depth_km": 0.0}, "no_labels", ("tectonic", "-")),
        ({"depth_km": 0.0, "dm_long_short": 1.0}, "catalogue_only", ("mass_movement", "R1")),
        ({"depth_km": 8.0, "dm_long_short": 1.0}, "catalogue_only", ("tectonic", "-")),
        ({"pub_lp_force": True}, "no_labels", ("mass_movement", "R1-pub")),
        ({"pub_lp_force": True}, "catalogue_only", ("tectonic", "-")),
        ({"pub_mt_class": "implosive_dominant"}, "no_labels", ("collapse", "R2-pub")),
        ({"depth_km": -2.5, "mt_iso_fraction": -0.46}, "catalogue_only", ("collapse", "R2-mt")),
        ({"depth_km": -2.5, "mt_iso_fraction": +0.6}, "catalogue_only", ("tectonic", "-")),
        ({"depth_km": 0.0, "preceded_by_larger_1h": 1.0}, "catalogue_only", ("collapse", "R2")),
        ({"depth_km": 10.0, "preceded_by_larger_1h": 1.0}, "catalogue_only", ("tectonic", "-")),
        (
            {
                "depth_km": 6.0,
                "n_m45_pm_half_year": 150,
                "cluster_median_dc": 25.0,
                "cluster_n_mt": 12,
            },
            "catalogue_only",
            ("caldera_collapse", "R4"),
        ),
        (
            {
                "depth_km": 6.0,
                "n_m45_pm_half_year": 150,
                "cluster_median_dc": 85.0,
                "cluster_n_mt": 12,
            },
            "catalogue_only",
            ("tectonic", "-"),
        ),
        (
            {
                "depth_km": 6.0,
                "n_m45_pm_half_year": 150,
                "cluster_median_dc": 25.0,
                "cluster_n_mt": 2,
            },
            "catalogue_only",
            ("tectonic", "-"),
        ),
        ({"in_catalogue": False}, "catalogue_only", ("not_in_catalogue", "-")),
    ],
)
def test_rules(row: dict, mode: str, expected: tuple[str, str]) -> None:
    assert D.classify(row, TH, mode) == expected


def test_bad_mode() -> None:
    with pytest.raises(ValueError):
        D.classify({}, TH, "magic")


def test_apply_and_scores() -> None:
    df = pd.DataFrame(
        [
            dict(
                case_id="A",
                expected_class="collapse",
                is_control=0,
                catalog_type="mine collapse",
                depth_km=-2.0,
                mt_iso_fraction=-0.5,
            ),
            dict(
                case_id="B",
                expected_class="mass_movement",
                is_control=0,
                catalog_type="landslide",
                depth_km=0.0,
            ),
            dict(case_id="C", expected_class="tectonic", is_control=0, depth_km=10.0),
            dict(case_id="X", expected_class="tectonic", is_control=1, depth_km=10.0),
        ]
    )
    out = D.apply(df, TH)
    sc = D.scores(out).set_index("mode")
    assert sc.loc["full", "case_hits"] == 3
    assert sc.loc["catalogue_only", "nontectonic_cases_detected"] == 1  # only the full-MT one
    assert sc.loc["full", "control_false_positives"] == 0
    assert set(D.confusion(out, "full").index) == {"collapse", "mass_movement", "tectonic"}


def test_thresholds_roundtrip() -> None:
    assert json.loads(json.dumps(TH.to_dict()))["iso_max"] == -0.3
