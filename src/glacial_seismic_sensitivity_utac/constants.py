"""Literature constants used for comparison and for the lag model.

GenesisAeon Package 133 (PROVISIONAL number - to be confirmed in PACKAGE_REGISTRY.md).
Companion of glacial-seismicity-utac (P101). Deliberately NO UTAC/CREP/AFET bridge.

Every number below is quoted from the cited source (checked 2026-10-10). Numbers marked
``via_abstract_or_snippet`` were read from abstracts/search excerpts, not from the full text.
"""

from __future__ import annotations

PACKAGE_ID = 133  # provisional
PACKAGE_ID_PROVISIONAL = True
COMPANION_PACKAGE = "glacial-seismicity-utac (P101)"


def _c(
    authors: str, year: int, title: str, journal: str, doi: str, note: str = ""
) -> dict[str, str]:
    return dict(authors=authors, year=str(year), title=title, journal=journal, doi=doi, note=note)


JOHNSON_2020 = _c(
    "Johnson, C.W., Fu, Y., Buergmann, R.",
    2020,
    "Hydrospheric modulation of stress and seismicity on shallow faults in southern Alaska",
    "Earth and Planetary Science Letters 530, 115904",
    "10.1016/j.epsl.2019.115904",
    "S Alaska, M>=2, <=40 km, declustered; ~10 kPa seasonal stress; 25 % rate increase ~3 months "
    "after normal-stress decrease; 3.5 % excess events per kPa. PRIOR ART for the SE Alaska "
    "seasonality reproduced here.",
)
JOHNSON_2020_PCT_PER_KPA = 3.5

SIRORATTANAKUL_AVOUAC_2026 = _c(
    "Sirorattanakul, K., Avouac, J.-P.",
    2026,
    "Seismic rhythms: Earthquake response to tectonic, hydrological, and tidal forcing in "
    "California",
    "Science Advances 12(13), eadz5711",
    "10.1126/sciadv.adz5711",
    "Seasonal modulation up to 15 %; a sigma 1-10 kPa (median 1.5); t_a 0.05-1 yr; background "
    "stressing ~30 kPa/yr; Parkfield modulation vanished after 2004 M6.",
)

DIETERICH_1994 = _c(
    "Dieterich, J.",
    1994,
    "A constitutive law for rate of earthquake production and its application to "
    "earthquake clustering",
    "J. Geophys. Res. 99(B2), 2601-2618",
    "10.1029/93JB02581",
)

BARLETTA_2018 = _c(
    "Barletta, V.R. et al.",
    2018,
    "Observed rapid bedrock uplift in Amundsen Sea Embayment promotes ice-sheet stability",
    "Science 360, 1335-1339",
    "10.1126/science.aao1447",
    "uplift up to 41 mm/yr; upper-mantle viscosity ~4e18 Pa s; GIA response decades to a century",
)
LARSEN_2005 = _c(
    "Larsen, C.F. et al.",
    2005,
    "Rapid viscoelastic uplift in southeast Alaska caused by post-Little Ice Age glacial retreat",
    "Earth Planet. Sci. Lett. 237, 548-560",
    "10.1016/j.epsl.2005.06.032",
    "uplift up to 32 mm/yr; asthenosphere ~3.7e19 Pa s (via_abstract_or_snippet)",
)
LARSEN_2004 = _c(
    "Larsen, C.F. et al.",
    2004,
    "Rapid uplift of southern Alaska caused by recent ice loss",
    "Geophys. J. Int. 158, 1118-1133",
    "10.1111/j.1365-246X.2004.02356.x",
    "eta_A = (1.4 +- 0.3)e19 Pa s (via_abstract_or_snippet)",
)
LANGE_2014 = _c(
    "Lange, H. et al.",
    2014,
    "Observed crustal uplift near the Southern Patagonian Icefield constrains improved "
    "viscoelastic Earth models",
    "Geophys. Res. Lett. 41",
    "10.1002/2013GL058419",
    "viscosity 1.6e18 or 8.0e18 Pa s; elastic lithosphere 36.5 km (via_abstract_or_snippet)",
)
PAGLI_2007 = _c(
    "Pagli, C., Sigmundsson, F. et al.",
    2007,
    "Glacio-isostatic deformation around the Vatnajokull ice cap, Iceland, induced by "
    "recent climate warming",
    "J. Geophys. Res. 112, B08405",
    "10.1029/2006JB004421",
    "elastic thickness 10-20 km; viscosity 4-10e18 Pa s (via_abstract_or_snippet)",
)
KHAN_2016 = _c(
    "Khan, S.A. et al.",
    2016,
    "Geodetic measurements reveal similarities between post-Last Glacial Maximum and "
    "present-day mass loss from the Greenland ice sheet",
    "Science Advances 2, e1600931",
    "10.1126/sciadv.1600931",
    "SE Greenland ~1e19 Pa s (via_abstract_or_snippet)",
)
MEY_2016 = _c(
    "Mey, J. et al.",
    2016,
    "Glacial isostatic uplift of the European Alps",
    "Nature Communications 7, 13382",
    "10.1038/ncomms13382",
    "upper-mantle viscosity 2.2 +- 0.5e20 Pa s for 50 km EET (via_abstract_or_snippet)",
)
HUGONNET_2021 = _c(
    "Hugonnet, R. et al.",
    2021,
    "Accelerated global glacier mass loss in the early twenty-first century",
    "Nature 592, 726-731",
    "10.1038/s41586-021-03436-z",
    "Iceland -0.88 m w.e./yr (2000-2019); Icelandic thinning 1.21 m/yr (2000-04) "
    "-> 0.77 m/yr (2015-19), 'North Atlantic anomaly'; Southern Andes -0.67; "
    "southern Arctic belt incl. Alaska -0.74 (accepted manuscript text)",
)
SWINDLES_2018 = _c(
    "Swindles, G.T. et al.",
    2018,
    "Climatic control on Icelandic volcanic activity during the mid-Holocene",
    "Geology 46(1), 47-50",
    "10.1130/G39633.1",
    "~600-yr lag between climate/glacier change and eruption frequency (online 2017, issue 2018)",
)
LOOMIS_2019 = _c(
    "Loomis, B.D., Luthcke, S.B., Sabaka, T.J.",
    2019,
    "Regularization and error characterization of GRACE mascons",
    "J. Geodesy 93, 1381-1398",
    "10.1007/s00190-019-01252-y",
    "GSFC RL06 mascons used for the load series",
)
ZALIAPIN_BENZION_2013 = _c(
    "Zaliapin, I., Ben-Zion, Y.",
    2013,
    "Earthquake clusters in southern California I",
    "J. Geophys. Res. 118, 2847-2864",
    "10.1002/jgrb.50179",
)
ADER_AVOUAC_2013 = _c(
    "Ader, T.J., Avouac, J.-P.",
    2013,
    "Detecting periodicities and declustering in earthquake catalogs using the Schuster spectrum",
    "Earth Planet. Sci. Lett. 377-378, 97-105",
    "10.1016/j.epsl.2013.06.032",
)

ALL_CITATIONS = {k: v for k, v in globals().items() if isinstance(v, dict) and "doi" in v}
