"""Literature constants used for comparison and for the lag model.

GenesisAeon Package 133, registry class KLIMA-KRYO-13 (entered in PACKAGE_REGISTRY.md 2026-10-10).
Companion of glacial-seismicity-utac (P101). Deliberately NO UTAC/CREP/AFET bridge.

Every number below is quoted from the cited source (checked 2026-10-10). Numbers marked
``via_abstract_or_snippet`` were read from abstracts/search excerpts, not from the full text.
"""

from __future__ import annotations

PACKAGE_ID = 133
PACKAGE_ID_PROVISIONAL = False
REGISTRY_CLASS = "KLIMA-KRYO-13"
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

# --- v0.1.0 extensions: tipping trajectories (A), quiescence (B), CSN, GNSS -----------------
EDWARDS_2021 = _c(
    "Edwards, T.L. et al.",
    2021,
    "Projected land ice contributions to twenty-first-century sea level rise",
    "Nature 593, 74-82",
    "10.1038/s41586-021-03302-y",
    "Table 1, 2015-2100, cm SLE, median [5-95 %], SSP5-8.5: Greenland 10 [2, 20]; glaciers "
    "16 [12, 21]; Antarctica 4 [-5, 14], risk-averse 22 [8, 43].",
)
EDWARDS_2021_CM = dict(greenland_ssp585=(10, 2, 20), glaciers_ssp585=(16, 12, 21))
DECONTO_2021 = _c(
    "DeConto, R.M. et al.",
    2021,
    "The Paris Climate Agreement and future sea-level rise from Antarctica",
    "Nature 593, 83-89",
    "10.1038/s41586-021-03427-0",
    "~3 degC: abrupt jump in the pace of Antarctic ice loss after ~2060, ~0.5 cm/yr GMSL by "
    "2100, an order of magnitude faster than today (abstract).",
)
ROBEL_2019 = _c(
    "Robel, A.A., Seroussi, H., Roe, G.H.",
    2019,
    "Marine ice sheet instability amplifies and skews uncertainty in projections of future "
    "sea-level rise",
    "PNAS 116(30), 14887-14892",
    "10.1073/pnas.1904822116",
)
IMBIE_2018 = _c(
    "The IMBIE team",
    2018,
    "Mass balance of the Antarctic Ice Sheet from 1992 to 2017",
    "Nature 558, 219-222",
    "10.1038/s41586-018-0179-y",
    "WAIS 53 +- 29 -> 159 +- 26 Gt/yr (1992-1997 -> 2012-2017).",
)
VELICOGNA_2020 = _c(
    "Velicogna, I. et al.",
    2020,
    "Continuity of ice sheet mass loss in Greenland and Antarctica from the GRACE and GRACE "
    "Follow-On missions",
    "Geophys. Res. Lett. 47, e2020GL087291",
    "10.1029/2020GL087291",
)
BEVIS_2019 = _c(
    "Bevis, M. et al.",
    2019,
    "Accelerating changes in ice mass within Greenland, and the ice sheet's sensitivity to "
    "atmospheric forcing",
    "PNAS 116(6), 1934-1939",
    "10.1073/pnas.1806562116",
)
BOERS_RYPDAL_2021 = _c(
    "Boers, N., Rypdal, M.",
    2021,
    "Critical slowing down suggests that the western Greenland Ice Sheet is close to a tipping "
    "point",
    "PNAS 118(21), e2024192118",
    "10.1073/pnas.2024192118",
)
ROBINSON_2012 = _c(
    "Robinson, A., Calov, R., Ganopolski, A.",
    2012,
    "Multistability and critical thresholds of the Greenland ice sheet",
    "Nature Climate Change 2, 429-432",
    "10.1038/nclimate1449",
)
LEVERMANN_WINKELMANN_2016 = _c(
    "Levermann, A., Winkelmann, R.",
    2016,
    "A simple equation for the melt elevation feedback of ice sheets",
    "The Cryosphere 10, 1799-1807",
    "10.5194/tc-10-1799-2016",
)
ARMSTRONG_MCKAY_2022 = _c(
    "Armstrong McKay, D.I. et al.",
    2022,
    "Exceeding 1.5 degC global warming could trigger multiple climate tipping points",
    "Science 377, eabn7950",
    "10.1126/science.abn7950",
)
OGATA_1988 = _c(
    "Ogata, Y.",
    1988,
    "Statistical models for earthquake occurrences and residual analysis for point processes",
    "J. Am. Stat. Assoc. 83(401), 9-27",
    "10.1080/01621459.1988.10478560",
)
OGATA_1992 = _c(
    "Ogata, Y.",
    1992,
    "Detection of precursory relative quiescence before great earthquakes through a "
    "statistical model",
    "J. Geophys. Res. 97(B13), 19845-19871",
    "10.1029/92JB00708",
)
WYSS_HABERMANN_1988 = _c(
    "Wyss, M., Habermann, R.E.",
    1988,
    "Precursory seismic quiescence",
    "Pure Appl. Geophys. 126, 319-332",
    "10.1007/BF00879001",
)
HABERMANN_1991 = _c(
    "Habermann, R.E.",
    1991,
    "Seismicity rate variations and systematic changes in magnitudes in teleseismic catalogs",
    "Tectonophysics 193, 277-289",
    "10.1016/0040-1951(91)90337-R",
)
HARRIS_1998 = _c(
    "Harris, R.A.",
    1998,
    "Introduction to special section: Stress triggers, stress shadows, and implications for "
    "seismic hazard",
    "J. Geophys. Res. 103(B10), 24347-24358",
    "10.1029/98JB01576",
)
HAMPEL_2010 = _c(
    "Hampel, A., Hetzel, R., Maniatis, G.",
    2010,
    "Response of faults to climate-driven changes in ice and water volumes on Earth's surface",
    "Phil. Trans. R. Soc. A 368, 2501-2517",
    "10.1098/rsta.2010.0031",
)
JOHNSTON_1987 = _c(
    "Johnston, A.C.",
    1987,
    "Suppression of earthquakes by large continental ice sheets",
    "Nature 330, 467-469",
    "10.1038/330467a0",
)
SCHORLEMMER_2005 = _c(
    "Schorlemmer, D., Wiemer, S., Wyss, M.",
    2005,
    "Variations in earthquake-size distribution across different stress regimes",
    "Nature 437, 539-542",
    "10.1038/nature04094",
)
SUNDAL_2011 = _c(
    "Sundal, A.V. et al.",
    2011,
    "Melt-induced speed-up of Greenland ice sheet offset by efficient subglacial drainage",
    "Nature 469, 521-524",
    "10.1038/nature09740",
)
TEDSTONE_2015 = _c(
    "Tedstone, A.J. et al.",
    2015,
    "Decadal slowdown of a land-terminating sector of the Greenland Ice Sheet despite warming",
    "Nature 526, 692-695",
    "10.1038/nature15722",
)
SIGMUNDSSON_2015 = _c(
    "Sigmundsson, F. et al.",
    2015,
    "Segmented lateral dyke growth in a rifting event at Bardarbunga volcanic system, Iceland",
    "Nature 517, 191-195",
    "10.1038/nature14111",
)
POTIN_2024 = _c(
    "Potin, B., Ruiz, S., Aden-Antoniow, F. et al.",
    2024,
    "A Revised Chilean Seismic Catalog from 1982 to Mid-2020",
    "Seismological Research Letters 96(1), 484-498",
    "10.1785/0220240047",
    "Data: Potin, Aden-Antoniow & Ruiz, Zenodo, doi:10.5281/zenodo.13146436 (CC BY 4.0).",
)
POTIN_2024_DATA = _c(
    "Potin, B., Aden-Antoniow, F., Ruiz, S.",
    2024,
    "Chilean Seismic Catalogue - 1982 - mid-2020",
    "Zenodo (DataCite)",
    "10.5281/zenodo.13146436",
    "Record rights: CC BY 4.0 and MIT (DataCite rightsList); concept DOI "
    "10.5281/zenodo.11360589. The README inside the zip cites 10.5281/zenodo.13146119, which "
    "does not resolve (checked 2026-10-10).",
)
BLEWITT_2018 = _c(
    "Blewitt, G., Hammond, W.C., Kreemer, C.",
    2018,
    "Harnessing the GPS data explosion for interdisciplinary science",
    "Eos 99",
    "10.1029/2018EO104623",
)

ALL_CITATIONS = {k: v for k, v in globals().items() if isinstance(v, dict) and "doi" in v}
