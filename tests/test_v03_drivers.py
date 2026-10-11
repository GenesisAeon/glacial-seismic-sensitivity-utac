"""v0.3: driver registry schema/rules and the S0 case list."""

from __future__ import annotations

import copy
import re

import pytest

from glacial_seismic_sensitivity_utac import drivers, v03_cases


@pytest.fixture(scope="module")
def reg() -> dict:
    return drivers.load()


def test_registry_valid(reg: dict) -> None:
    assert drivers.validate(reg, drivers.verified_dois()) == []


def test_registry_has_open_topics(reg: dict) -> None:
    ids = {e["id"] for e in reg["drivers"]}
    # gaps the user asked to fill: hydrates, karst, permafrost, salt caverns
    assert {"D-HYD", "D-KARST", "D-PERMA", "D-SALT"} <= ids
    # only the P133 core driver is active
    assert [e["id"] for e in reg["drivers"] if e["status"] == "active"] == ["D-GLAC"]


def _one(reg: dict, **kw: object) -> dict:
    r = copy.deepcopy(reg)
    r["drivers"][1].update(kw)
    return r


@pytest.mark.parametrize(
    ("change", "rule"),
    [
        ({"sources": []}, "rule 1"),
        ({"sources": ["10.9999/not-verified"]}, "rule 1"),
        ({"status": "active", "prereg": "exploratory"}, "rule 2"),
        ({"status": "rejected", "notes": ""}, "rule 3"),
        ({"origin": "ai_report", "evidence": "reported"}, "rule 4"),
        ({"evidence": "proven"}, "evidence must"),
        ({"prereg": "maybe"}, "prereg must"),
    ],
)
def test_registry_rules_fire(reg: dict, change: dict, rule: str) -> None:
    errs = drivers.validate(_one(reg, **change), drivers.verified_dois())
    assert any(rule in e for e in errs), errs


def test_registry_duplicate_and_missing(reg: dict) -> None:
    r = copy.deepcopy(reg)
    r["drivers"].append(copy.deepcopy(r["drivers"][0]))
    del r["drivers"][2]["notes"]
    errs = drivers.validate(r)
    assert any("duplicate id" in e for e in errs)
    assert any("missing" in e for e in errs)


def test_verified_dois_wellformed() -> None:
    v = drivers.verified_dois()
    assert len(v) >= 30
    assert all(re.match(r"^10\.\d{4,9}/\S+$", d) for d in v)


def test_case_list_consistent() -> None:
    v = drivers.verified_dois()
    ranks = [c.rank for c in v03_cases.CASES if c.rank is not None]
    assert ranks == list(range(1, 9))
    top5 = [c.case_id for c in v03_cases.CASES[:5]]
    assert top5 == ["crandall_2007", "bingham_2013", "langtang_2026", "groningen", "lorca_2011"]
    for c in v03_cases.CASES:
        assert c.expected_class in v03_cases.SOURCE_CLASSES
        for p in c.published:
            assert p.doi.lower() in v, p.doi
    assert v03_cases.case_by_id("langtang_2026").expected_class == "mass_movement"
    assert v03_cases.case_by_id("budhi_gandaki_2026").status == "watchlist"
    with pytest.raises(KeyError):
        v03_cases.case_by_id("nope")
    assert v03_cases.s0_payload()["step"] == "S0"


def test_s0_amendment_a1() -> None:
    v = drivers.verified_dois()
    ids = [c.case_id for c in v03_cases.CASES_A1]
    assert ids == ["napoleonville_2012", "kilauea_2018"]
    for c in v03_cases.CASES_A1:
        assert c.expected_class in v03_cases.SOURCE_CLASSES
        assert all(p.doi.lower() in v for p in c.published)
    # the frozen S0 payload must not contain the A1 cases
    frozen = [c["case_id"] for c in v03_cases.s0_payload()["cases"]]
    assert not set(ids) & set(frozen)
    assert v03_cases.case_by_id("kilauea_2018").rank == 10
