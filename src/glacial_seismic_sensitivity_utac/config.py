"""Pre-registered analysis parameters and region definitions.

All values below were fixed before the confirmatory analyses were run (first
run 2026-10-10). Changing any of them after looking at new data invalidates
the confirmatory status of the corresponding test (see PREREGISTRATION.md).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths (overridable via environment variables so tests can use temp dirs)
# ---------------------------------------------------------------------------
ROOT = Path(os.environ.get("GSS_ROOT", Path(__file__).resolve().parents[2]))
RAW = Path(os.environ.get("GSS_RAW", ROOT / "data" / "raw"))
OUT = Path(os.environ.get("GSS_OUT", ROOT / "results"))
CHARTS = Path(os.environ.get("GSS_CHARTS", ROOT / "charts"))

START = "1990-01-01"
END = os.environ.get("GSS_END", "2026-10-10T23:59:59")  # extend for confirmatory runs
TEST_END_YEAR = 2025  # last complete year used in exploratory/retrospective tests
CONFIRMATORY_START = "2026-11-01"  # data from here on are reserved for confirmatory tests

Group = str  # "mountain", "icesheet", "control"


@dataclass(frozen=True)
class Region:
    """A study region: lat/lon box, data source and group label."""

    name: str
    box: tuple[float, float, float, float]  # (minlat, maxlat, minlon, maxlon)
    group: Group
    source: str  # comcat | comcat_ak | sed | geonet | imo | geus
    minmag: float = 3.0
    maxdepth: float | None = None
    pair: str | None = None  # network-internal comparison pair id
    exclude: str | None = None
    note: str = ""
    grace: bool = True
    last_year: int | None = None  # last complete catalogue year if the source ends early

    @property
    def raw_file(self) -> Path:
        return RAW / f"{self.source}_{self.name}_M{self.minmag}.csv"


_R = [
    # --- fast-shrinking mountain glaciers ("critical window") ---------------
    Region("SE_Alaska", (57.0, 61.5, -145.0, -133.0), "mountain", "comcat", 3.0),
    Region(
        "SE_Alaska_AK",
        (57.0, 61.5, -145.0, -133.0),
        "mountain",
        "comcat_ak",
        1.5,
        40.0,
        pair="AK",
        note="Alaska Earthquake Center (net=ak) contributions via ComCat",
    ),
    Region("Alps", (43.5, 48.5, 5.0, 16.5), "mountain", "comcat", 3.0),
    Region(
        "Alps_SED",
        (45.4, 47.0, 6.0, 10.5),
        "mountain",
        "sed",
        1.0,
        40.0,
        pair="SED",
        note="Swiss Seismological Service FDSN; glaciated Swiss/Western Alps",
    ),
    Region("Patagonia", (-56.0, -45.0, -77.0, -66.0), "mountain", "comcat", 3.0),
    Region("Himalaya_Karakoram", (27.0, 37.0, 72.0, 92.0), "mountain", "comcat", 3.0),
    Region(
        "NZ_Southern_Alps",
        (-45.5, -42.0, 168.0, 172.5),
        "mountain",
        "geonet",
        1.5,
        40.0,
        pair="GEONET",
        note="GeoNet FDSN",
    ),
    Region(
        "Iceland",
        (62.5, 67.5, -25.5, -12.5),
        "mountain",
        "comcat",
        3.0,
        note="Iceland ice caps; volcanic seismicity dominates",
    ),
    Region(
        "Iceland_Vatnajokull_IMO",
        (63.9, 64.9, -18.5, -15.3),
        "mountain",
        "imo",
        0.5,
        40.0,
        note="IMO API; record available only from mid-2010s (see results)",
    ),
    # --- great ice sheets ----------------------------------------------------
    Region(
        "Greenland", (59.0, 84.0, -75.0, -20.0), "icesheet", "comcat", 3.0, exclude="lon>-36&lat<66"
    ),
    Region(
        "Greenland_GEUS",
        (59.0, 84.0, -75.0, -10.0),
        "icesheet",
        "geus",
        0.0,
        exclude="lon>-36&lat<66",
        note="GEUS GeoJSON catalogue",
    ),
    Region("West_Antarctica", (-80.0, -70.0, -130.0, -85.0), "icesheet", "comcat", 3.0),
    # --- non-glaciated controls ------------------------------------------------
    Region("Philippines", (4.0, 21.0, 116.0, 128.0), "control", "comcat", 3.0),
    Region("Indonesia", (-11.0, 6.0, 94.0, 141.0), "control", "comcat", 3.0),
    Region("Japan", (30.0, 46.0, 128.0, 147.0), "control", "comcat", 3.0),
    Region("Central_America", (7.0, 18.0, -93.0, -82.0), "control", "comcat", 3.0),
    Region("Central_Andes", (-35.0, -15.0, -76.0, -66.0), "control", "comcat", 3.0),
    Region(
        "Interior_AK_ctrl",
        (63.0, 66.0, -152.0, -144.0),
        "control",
        "comcat_ak",
        1.5,
        40.0,
        pair="AK",
    ),
    Region(
        "N_Switzerland_ctrl",
        (47.0, 48.0, 6.0, 10.0),
        "control",
        "sed",
        1.0,
        40.0,
        pair="SED",
        note="Jura/Molasse, same SED network, not glaciated",
    ),
    Region(
        "Central_Andes_CSN_ctrl",
        (-35.0, -18.0, -76.0, -66.0),
        "control",
        "csn_zenodo",
        0.0,
        40.0,
        pair="CSN",
        note="relocated CSN catalogue 1982-mid-2020 (Potin et al. 2024, Zenodo 13146436); "
        "national-tier counterpart of the ComCat Central_Andes control; ends mid-2020",
        last_year=2019,
    ),
    Region(
        "NZ_Wellington_ctrl",
        (-41.8, -39.5, 174.3, 176.8),
        "control",
        "geonet",
        1.5,
        40.0,
        pair="GEONET",
        note="lower North Island, same GeoNet network, not glaciated",
    ),
]
REGIONS: dict[str, Region] = {r.name: r for r in _R}


def main_regions() -> list[str]:
    """Regions with a catalogue running to TEST_END_YEAR (enter F1-F3, criticality, C1)."""
    return [n for n, r in REGIONS.items() if r.last_year is None]


# Extra GRACE boxes used only by the tipping / precursor module (no catalogue attached)
EXTRA_GRACE_BOXES: dict[str, tuple[tuple[float, float, float, float], str | None]] = {
    "Amundsen_ASE": ((-80.0, -72.0, -120.0, -95.0), None),
    "Greenland_all": ((59.0, 84.0, -75.0, -10.0), "lon>-36&lat<66"),
    "Greenland_SE_box": ((60.0, 68.0, -50.0, -30.0), None),
    "Greenland_W_box": ((64.0, 72.0, -56.0, -45.0), None),
    "SE_Alaska_box": ((57.0, 61.5, -145.0, -133.0), None),
    "Vatnajokull": ((63.9, 64.9, -18.5, -15.3), None),
    "Patagonia_box": ((-56.0, -45.0, -77.0, -66.0), None),
}

# Nevada Geodetic Laboratory GNSS time series (Blewitt, Hammond & Kreemer 2018,
# doi:10.1029/2018EO104623), IGS20 frame, daily tenv3 files.
NGL_TENV3 = "https://geodesy.unr.edu/gps_timeseries/IGS20/tenv3/IGS20/{sta}.tenv3"
NGL_STEPS = "https://geodesy.unr.edu/NGLStationPages/steps.txt"
GNSS_STATIONS: dict[str, tuple[str, str]] = {
    # station: (region / ice mass, role)
    "HOFN": ("Iceland (Vatnajokull, SE margin)", "glacier"),
    "KULU": ("SE Greenland (Kulusuk)", "icesheet"),
    "QAQ1": ("S Greenland (Qaqortoq)", "icesheet"),
    "KELY": ("W Greenland (Kangerlussuaq)", "icesheet"),
    "SCOR": ("E Greenland (Scoresbysund)", "icesheet"),
    "THU2": ("NW Greenland (Thule)", "icesheet"),
    "AB50": ("SE Alaska (Juneau area)", "glacier"),
    "JNU1": ("SE Alaska (Juneau)", "glacier"),
    "TOMO": ("Amundsen Sea Embayment (POLENET)", "icesheet"),
    "BACK": ("Amundsen Sea Embayment (POLENET)", "icesheet"),
    "INMN": ("Amundsen Sea Embayment (POLENET)", "icesheet"),
    "LPLY": ("Amundsen/Bellingshausen (POLENET)", "icesheet"),
    "COYQ": ("Aysen, Chile (Coyhaique, N of the N Patagonian Icefield)", "glacier"),
    "FAIR": ("Interior Alaska (Fairbanks) - control", "control"),
}

# Chilean CSN relocated catalogue (Potin et al. 2024, SRL 96(1):484-498,
# doi:10.1785/0220240047; data doi:10.5281/zenodo.13146436, CC BY 4.0)
CSN_ZENODO_ZIP = (
    "https://zenodo.org/api/records/13146436/files/"
    "chilean_seismic_catalogue-1982-2020-publication_release.zip/content"
)
CSN_ZENODO_MD5 = "49d78f37784956e362de82d159083165"

GROUP_LABEL = {"mountain": "Gebirgsgletscher", "icesheet": "Eisschild", "control": "Kontrolle"}

# ---------------------------------------------------------------------------
# Catalog statistics
# ---------------------------------------------------------------------------
MC_CORRECTION = 0.2  # MAXC + 0.2 (Woessner & Wiemer 2005)
MC_REF_QUANTILE = 0.9  # reference Mc = 90th percentile of yearly Mc
DM = 0.1
B_MIN_EVENTS = 50
BIN_YEARS = 2
MAX_EVENTS_DECLUSTER = 60000  # guard against runaway runtimes

# Zaliapin & Ben-Zion (2013) nearest-neighbour parameters
NN_DF = 1.6
NN_B = 1.0
NN_W = 0.5
NN_MAX_PARENTS = 5000

# Critical slowing down (Dakos et al. 2012)
DETREND_BANDWIDTH_MONTHS = 24
ROLL_FRACTION = 0.5
N_SURROGATES = int(os.environ.get("GSS_N_SURROGATES", 2000))
N_BLOCK_PERM = int(os.environ.get("GSS_N_PERM", 10000))
BLOCK_LEN = 2
ALPHA = 0.05
CITY_POP = 100_000
CITY_RADIUS_KM = 100.0
SWARM_MIN_SIZE = 5
SEED = 20261010

# ---------------------------------------------------------------------------
# Sensitivity ("Fruehstadium") tests -- pre-registered
# ---------------------------------------------------------------------------
SENS_REF_YEAR = 2008.0  # centring of the time interaction
SENS_LAG_MONTHS_PRIMARY = 3  # Johnson, Fu & Buergmann (2020): ~3-month lag in southern Alaska
SENS_LAGS_EXPLORATORY = (0, 1, 2, 4, 5, 6)
SENS_MIN_EVENTS = 300  # minimum declustered events for a region to enter F-tests
SENS_N_PERM = int(os.environ.get("GSS_N_PERM_SENS", 2000))
G_ACC = 9.81
RHO_WATER = 1000.0

# Confirmatory design (frozen 2026-10-10)
CONFIRM_ALPHA_INTERIM = 0.01  # look 1: data 2026-11-01 .. 2029-10-31
CONFIRM_ALPHA_FINAL = 0.04  # look 2: data 2026-11-01 .. 2036-10-31


PRECIP_POINTS: dict[str, list[tuple[float, float]]] = {
    # coastal glaciated SE Alaska: Yakutat, Glacier Bay, Juneau icefield, Icy Bay, Cordova
    "SE_Alaska_AK": [
        (59.55, -139.7),
        (58.8, -136.5),
        (58.6, -134.3),
        (60.0, -141.5),
        (60.5, -145.0),
        (59.2, -137.5),
    ],
    "Interior_AK_ctrl": [
        (64.8, -147.7),
        (63.7, -149.0),
        (64.0, -151.0),
        (65.5, -148.0),
        (64.5, -145.5),
    ],
    "Alps_SED": [(46.5, 8.0), (46.0, 7.5), (46.6, 9.8), (45.9, 6.9), (46.8, 8.6)],
    "N_Switzerland_ctrl": [(47.4, 7.5), (47.5, 8.5), (47.2, 7.0), (47.6, 9.3)],
    "NZ_Southern_Alps": [(-43.5, 170.2), (-44.0, 169.5), (-43.0, 171.0), (-44.7, 168.5)],
    "NZ_Wellington_ctrl": [(-41.2, 174.9), (-40.4, 175.6), (-39.9, 176.3), (-41.0, 175.5)],
}
