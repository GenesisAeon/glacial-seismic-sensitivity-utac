"""Frozen b-value of the primary pair (P133, draft A8): hash pin, snapshots, no 2026 data."""

from __future__ import annotations

import gzip
import hashlib
import json

import pandas as pd
import pytest

from glacial_seismic_sensitivity_utac.etas_adequacy import PRIMARY_PAIR, load_baselines
from glacial_seismic_sensitivity_utac.etas_adequacy.forecast import expected_cluster_moments
from glacial_seismic_sensitivity_utac.etas_adequacy.frozen import (
    B_VALUE_PATH,
    FrozenFileError,
    load_b_values,
)

DOC = json.loads(B_VALUE_PATH.read_bytes())


def test_frozen_b_values_load_and_are_plausible() -> None:
    b = load_b_values()
    assert tuple(b) == PRIMARY_PAIR
    assert b["SE_Alaska_AK"] == pytest.approx(0.913, abs=5e-4)
    assert b["Interior_AK_ctrl"] == pytest.approx(0.945, abs=5e-4)


def test_tampered_copy_is_rejected(tmp_path) -> None:  # type: ignore[no-untyped-def]
    f = tmp_path / "b.json"
    f.write_bytes(B_VALUE_PATH.read_bytes().replace(b'"b": 0.9', b'"b": 0.8', 1))
    with pytest.raises(FrozenFileError, match="SHA-256"):
        load_b_values(f)


@pytest.mark.parametrize("region", PRIMARY_PAIR)
def test_snapshot_matches_its_hashes_and_contains_no_2026_event(region: str) -> None:
    rec = DOC["regions"][region]
    gz = (B_VALUE_PATH.parent / rec["snapshot"]).read_bytes()
    raw = gzip.decompress(gz)
    assert hashlib.sha256(gz).hexdigest() == rec["snapshot_sha256_gz"]
    assert hashlib.sha256(raw).hexdigest() == rec["snapshot_sha256_csv"]
    t = pd.to_datetime(pd.Series(raw.decode().splitlines()[1:]).str.split(",").str[0], utc=True)
    assert t.min() >= pd.Timestamp("2016-01-01", tz="UTC")
    assert t.max() < pd.Timestamp("2026-01-01", tz="UTC")
    assert len(t) == rec["n_events_downloaded"]


def test_both_regions_stay_subcritical_with_the_frozen_b() -> None:
    models, b = load_baselines(), load_b_values()
    for region in PRIMARY_PAIR:
        n, _ = expected_cluster_moments(models[region], b[region], 8.0)
        assert n == pytest.approx(DOC["regions"][region]["branching_ratio_b_hat"])
        assert n < 1.0
