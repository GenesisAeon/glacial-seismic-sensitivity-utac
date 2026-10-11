"""v0.3 mass-change / collapse module: case list (S0) and tectonic controls.

Everything in this module is *exploratory design input* for v0.3 (steps S0-S2). It does not
touch any frozen v0.1/v0.2 parameter. The case list is frozen in S0 by writing
``results/v03/s0_case_list.json`` (see scripts/v03_freeze_s0.py) and recording its SHA-256 in
docs/v03/S0_FALLLISTE.md; after that, changes need a dated, justified amendment.

Source classes (physical source type of the *key event*, not its trigger):
  mass_movement      surface mass movement (rock avalanche, landslide, ice-rock avalanche)
  collapse           roof / cavity collapse (mine, post-explosion cavity)
  caldera_collapse   magma-withdrawal caldera collapse (rim faulting, strongly non-DC)
  tectonic           shear slip on a fault; may be triggered or modulated by anthropogenic or
                     hydrological forcing (reservoir, gas production, groundwater) -- that is a
                     separate *forcing* axis, not a different source class.

All published values carry the DOI they were taken from; DOIs were resolved via Crossref on
2026-10-11. Values not given in a resolvable source are not entered.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

SOURCE_CLASSES = ("mass_movement", "collapse", "caldera_collapse", "tectonic")


@dataclass(frozen=True)
class Published:
    """One published value for a case, with the DOI it comes from."""

    key: str
    value: Any
    doi: str
    note: str = ""


@dataclass(frozen=True)
class Query:
    """Catalogue snapshot definition (S1)."""

    name: str
    service: str  # comcat | knmi | emsc
    lat: float
    lon: float
    radius_km: float
    start: str
    end: str
    minmag: float | None = None


@dataclass(frozen=True)
class Case:
    case_id: str
    rank: int | None  # None = watchlist / control
    name: str
    expected_class: str  # one of SOURCE_CLASSES
    forcing: str  # free text: anthropogenic / hydrological forcing context
    status: str  # core | core_limited | watchlist
    lat: float
    lon: float
    radius_km: float
    key_event_ids: tuple[str, ...]  # catalogue ids (ComCat) of the key event(s); may be empty
    key_event_rule: str  # how the key event is chosen if ids are not fixed
    queries: tuple[Query, ...]
    published: tuple[Published, ...] = field(default_factory=tuple)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


END = "2026-10-01T00:00:00"  # last day included in S1 snapshots (before C1 window opens)

CASES: tuple[Case, ...] = (
    Case(
        "crandall_2007",
        1,
        "Crandall Canyon coal mine collapse, Utah, 2007-08-06",
        "collapse",
        "underground coal mining (room-and-pillar retreat)",
        "core",
        39.4642,
        -111.2168,
        15.0,
        ("uu50342430",),
        "fixed ComCat id (type 'mine collapse')",
        (Query("crandall_comcat", "comcat", 39.4642, -111.2168, 30.0, "1990-01-01", END),),
        (
            Published("ML", 3.9, "10.1785/gssrl.79.5.637", "local magnitude, 08:48:40 UTC"),
            Published("Mw", 4.1, "10.1002/2014jb011037", "recorded as an Mw 4.1 event"),
            Published(
                "mt_class",
                "implosive_dominant",
                "10.1126/science.1157392",
                "dominated by an implosive component; smaller non-collapse component",
            ),
            Published(
                "precursor",
                "b-value and location changes in the 48 h before the collapse "
                "(template matching, Mc 0.0)",
                "10.1002/2014jb011037",
            ),
        ),
        "ComCat depth -2.5 km (above sea level datum); the mine district has continuous "
        "mining-induced background seismicity.",
    ),
    Case(
        "bingham_2013",
        2,
        "Bingham Canyon mine rock avalanches, Utah, 2013-04-11 UTC",
        "mass_movement",
        "open-pit mining (slope failure)",
        "core",
        40.536,
        -112.142,
        10.0,
        (),
        "published origin times 03:30:22 and 05:05:22 UTC; the two slides are NOT ComCat "
        "events (checked 2026-10-11) -> key-event features from the publication",
        (Query("bingham_comcat", "comcat", 40.536, -112.142, 20.0, "1990-01-01", END),),
        (
            Published(
                "origin_times_utc",
                ["2013-04-11T03:30:22", "2013-04-11T05:05:22"],
                "10.1130/gsatg191a.1",
            ),
            Published("ML", [2.5, 2.4], "10.1130/gsatg191a.1"),
            Published("md_min", 3.5, "10.1130/gsatg191a.1", "duration magnitudes '>3.5'"),
            Published(
                "followup_events_6d", 16, "10.1130/gsatg191a.1", "impulsive arrivals, tectonic-like"
            ),
            Published(
                "lp_force_history",
                True,
                "10.1002/2014gl060592",
                "long-period force inversion (single-force source)",
            ),
            Published("volume_Mm3", 52, "10.1002/2016jf004036"),
        ),
    ),
    Case(
        "langtang_2026",
        3,
        "Langtang ice/rock mass movement, Nepal, 2026-08-26",
        "mass_movement",
        "none known (high-mountain mass movement)",
        "core",
        28.271,
        85.515,
        50.0,
        ("us7000tbwb", "us7000tc90"),
        "fixed ComCat ids (type 'landslide', Ms_vx)",
        (Query("langtang_comcat", "comcat", 28.271, 85.515, 100.0, "2000-01-01", END),),
        (),
        "Own class 'Massenbewegungsquelle' (approved 2026-10-11). No peer-reviewed source yet; "
        "ComCat event pages are the only source.",
    ),
    Case(
        "groningen",
        4,
        "Groningen gas field induced seismicity, NL",
        "tectonic",
        "gas production (reservoir compaction); production stopped 2023/24",
        "core",
        53.30,
        6.75,
        30.0,
        (),
        "largest KNMI event inside the field polygon proxy (30 km around 53.30N 6.75E)",
        (
            Query("groningen_knmi", "knmi", 53.30, 6.75, 30.0, "1986-01-01", END),
            Query("groningen_comcat", "comcat", 53.30, 6.75, 30.0, "1986-01-01", END),
        ),
        (
            Published(
                "first_event",
                "1991-12-05 ML 2.4 Middelstum",
                "10.1190/tle34060664.1",
                "also in the KNMI snapshot",
            ),
            Published("context", "seismicity development and hazard", "10.1017/njg.2017.20"),
        ),
        "Forcing series (monthly production) not obtained by a sanctioned open route yet "
        "-> forcing coupling not tested in S2 (decision needed).",
    ),
    Case(
        "lorca_2011",
        5,
        "Lorca earthquake, SE Spain, 2011-05-11 (Mw 5.1)",
        "tectonic",
        "long-term groundwater extraction (crustal unloading)",
        "core",
        37.699,
        -1.672,
        15.0,
        ("usp000j1en",),
        "fixed ComCat id (mainshock); foreshock usp000j1ea",
        (
            Query("lorca_comcat", "comcat", 37.699, -1.672, 30.0, "1990-01-01", END),
            Query("lorca_emsc", "emsc", 37.699, -1.672, 30.0, "2004-10-01", END),
        ),
        (
            Published(
                "forcing",
                "slip distribution controlled by groundwater unloading",
                "10.1038/ngeo1610",
            ),
        ),
        "Negative case for the source discriminator (tectonic source, anthropogenic modulation).",
    ),
    Case(
        "punggye_2017",
        6,
        "Punggye-ri post-explosion collapse, DPRK, 2017-09-03",
        "collapse",
        "underground nuclear explosion 8.5 min earlier (us2000aert)",
        "core",
        41.332,
        129.030,
        20.0,
        ("us2000aetk",),
        "fixed ComCat id (type 'collapse'); trigger us2000aert (type 'nuclear explosion')",
        (Query("punggye_comcat", "comcat", 41.30, 129.08, 50.0, "2006-01-01", END),),
        (
            Published("mb_explosion_collapse", [6.1, 4.1], "10.1785/0220180130"),
            Published(
                "mt_class",
                "closing_crack_plus_vertical_force",
                "10.1785/0220180130",
                "MT not a pure implosion; tensional closing crack + two-sided vertical force",
            ),
            Published("full_mt", "full MT analysis of all DPRK tests", "10.1785/0220180158"),
        ),
        "Explosion class itself is out of scope; only the collapse is a module case.",
    ),
    Case(
        "bardarbunga_2014",
        7,
        "Bárðarbunga caldera collapse, Iceland, 2014-08-16 to 2015-02-27",
        "caldera_collapse",
        "magma withdrawal via a 48 km dike (Holuhraun eruption)",
        "core",
        64.64,
        -17.53,
        15.0,
        (),
        "all ComCat events M>=5.0 within 15 km of the caldera, 2014-08-16..2015-02-28",
        (Query("bardarbunga_comcat", "comcat", 64.64, -17.53, 20.0, "1990-01-01", END),),
        (
            Published(
                "caldera_subsidence",
                "110 km2, 65 m deep, gradual, ~180 d",
                "10.1126/science.aaf8988",
            ),
            Published("mt_class", "highly non-double-couple rim earthquakes", "10.1093/gji/ggv157"),
            Published("aseismic", "majority of subsidence aseismic", "10.1093/gji/ggv157"),
            Published(
                "dike_mt", "dike seismicity strike-slip; no non-DC events", "10.1002/2015gl067423"
            ),
            Published("dike", "segmented lateral dike growth", "10.1038/nature14111"),
        ),
    ),
    Case(
        "koyna",
        8,
        "Koyna-Warna reservoir-triggered seismicity, India (1967 M6.3)",
        "tectonic",
        "reservoir impoundment and level changes (no open level series)",
        "core_limited",
        17.20,
        73.75,
        40.0,
        ("iscgem828259",),
        "fixed ComCat/ISC-GEM id (1967-12-10)",
        (Query("koyna_comcat", "comcat", 17.20, 73.75, 60.0, "1960-01-01", END),),
        (
            Published(
                "review",
                "reservoir-triggered seismicity, Koyna emphasis",
                "10.1016/s0012-8252(02)00063-6",
            ),
            Published("review_2022", "Koyna as RTS site", "10.1007/s12040-021-01780-2"),
        ),
        "Catalogue-only (ComCat completeness is poor for M<4); forcing not testable without "
        "reservoir-level data.",
    ),
    Case(
        "budhi_gandaki_2026",
        None,
        "Budhi Gandaki flood / landslide-dam event, Nepal, 2026-10-11 (watchlist only)",
        "mass_movement",
        "unconfirmed (landslide dam reported)",
        "watchlist",
        28.45,
        84.85,
        50.0,
        (),
        "none (no ComCat event as of 2026-10-11)",
        (
            Query(
                "budhi_gandaki_comcat",
                "comcat",
                28.45,
                84.85,
                60.0,
                "2026-09-01",
                "2026-10-11T23:59:59",
            ),
        ),
        (),
        "Not evaluated; cause unconfirmed; recorded only to document the null catalogue result.",
    ),
)

# Tectonic control regions: every ComCat 'earthquake' M>=4.5 mainshock 2000-2026 in these
# boxes is a control key event with expected class 'tectonic'. (minlat, maxlat, minlon, maxlon)
CONTROL_REGIONS: dict[str, tuple[float, float, float, float]] = {
    "Utah_Intermountain": (36.5, 42.5, -114.5, -108.5),
    "Nepal_Himalaya": (26.0, 31.0, 80.0, 89.0),
    "Iceland": (63.0, 67.5, -25.0, -13.0),
    "SE_Spain": (36.0, 39.5, -4.0, 0.0),
    "Korea_NE_China": (37.0, 44.0, 124.0, 132.0),
    "W_India": (15.0, 21.0, 72.0, 76.0),
}
CONTROL_START = "2000-01-01"
CONTROL_MINMAG_FETCH = 2.5
CONTROL_MAINSHOCK_MIN = 4.5
# Control events that are part of a case sequence are excluded (radius around case centres).
CONTROL_EXCLUDE_KM = 25.0
NAMED_CONTROLS = {"Magna_2020": "uu60363602"}

WATCHLIST_NOT_EVALUATED = ("budhi_gandaki_2026",)

OPTIONAL_CASES_PROPOSED = {
    "napoleonville_2012": (
        "salt-cavern sinkhole; MT with large volume-INCREASE components 61-82 % (not implosive)",
        "10.1785/0120130260",
    ),
    "kilauea_2018": (
        "caldera collapse with repeated Mw~5 collapse events; coupled shear + crack closure",
        "10.1029/2019GL085636",
    ),
}


def case_by_id(case_id: str) -> Case:
    for c in CASES:
        if c.case_id == case_id:
            return c
    raise KeyError(case_id)


def s0_payload() -> dict[str, Any]:
    """Machine-readable S0 case list (what gets frozen)."""
    return {
        "module": "v0.3 mass-change / collapse",
        "step": "S0",
        "source_classes": list(SOURCE_CLASSES),
        "cases": [c.to_dict() for c in CASES],
        "control_regions": {k: list(v) for k, v in CONTROL_REGIONS.items()},
        "control_start": CONTROL_START,
        "control_minmag_fetch": CONTROL_MINMAG_FETCH,
        "control_mainshock_min": CONTROL_MAINSHOCK_MIN,
        "control_exclude_km": CONTROL_EXCLUDE_KM,
        "named_controls": NAMED_CONTROLS,
        "snapshot_end": END,
        "optional_cases_proposed": {k: list(v) for k, v in OPTIONAL_CASES_PROPOSED.items()},
    }
