# Daten und Katalogabdeckung

Rohdaten werden **nicht** eingecheckt (`data/raw/` steht in `.gitignore`). Neu erzeugen mit
`glacial-sensitivity fetch`. Abrufstand: **2026-10-10**. Analysiert wird bis **2025-12-31**; das Teiljahr
2026 fließt in keinen Test ein.

## Quellen

| Quelle | Endpunkt | Verwendung | Lizenz/Hinweis |
|---|---|---|---|
| USGS ComCat | https://earthquake.usgs.gov/fdsnws/event/1/ | globale Boxen M ≥ 3 (Abruf ab M 3, Mc individuell); `catalog=ak` → Beiträge des Alaska Earthquake Center (AEC) | gemeinfrei (USGS) |
| Schweizerischer Erdbebendienst (SED) | https://eida.ethz.ch/fdsnws/event/1/ (der Arclink-Endpunkt antwortete nicht) | Alpen-Kernbox und Nordschweiz-Kontrolle, M ≥ 1, ≤ 40 km | Nutzungsbedingungen SED |
| GeoNet (Neuseeland) | https://service.geonet.org.nz/fdsnws/event/1/ | Südalpen und Wellington-Kontrolle, M ≥ 1,5, ≤ 40 km | siehe GeoNet-Datenpolitik |
| Veðurstofa Íslands (IMO) | https://api.vedur.is/quakes/events | Vatnajökull, `system=sil` (Altsystem mit Daten ab 1991; das Standardsystem SeisComP liefert nur jüngere Daten), Polygonfilter | CC BY 4.0 |
| GEUS (Grönland) | https://seismologi.geus.dk/geojson/GeoJSON-eqs.json | Grönland, nur „Confirmed earthquake“ | GEUS |
| CSN Chile (FDSN) | https://eew.csn.uchile.cl/fdsnws/event/1/query | **nicht nutzbar**: HTTP 204 für alle getesteten Zeitfenster | – |
| CSN Chile, relokalisierter Katalog 1982–Mitte 2020 (ab v0.1.0) | https://zenodo.org/records/13146436 (Zip, md5 `49d78f37784956e362de82d159083165`) | Kontrolle `Central_Andes_CSN_ctrl` (35–18° S, ≤ 40 km), nur 1990–2019, getrennt vom Hauptlauf | CC BY 4.0 (DataCite listet zusätzlich MIT). Zitieren: Potin et al. 2024, SRL 96(1), 484–498, doi:10.1785/0220240047, und Daten doi:10.5281/zenodo.13146436 |
| Nevada Geodetic Laboratory GNSS (ab v0.1.0) | https://geodesy.unr.edu/gps_timeseries/IGS20/tenv3/IGS20/{STA}.tenv3 und https://geodesy.unr.edu/NGLStationPages/steps.txt | Hebungsrate und -beschleunigung an 14 Stationen (M2) | Blewitt, Hammond & Kreemer 2018, doi:10.1029/2018EO104623 |
| GRACE/GRACE-FO GSFC Mascons RL06 v2.0 | https://earth.gsfc.nasa.gov/geo/data/grace-mascons | Monatliche Last 2002-04 bis 2026-03 | Loomis et al. 2019, doi:10.1007/s00190-019-01252-y |
| ERA5 über Open-Meteo-Archiv | https://archive-api.open-meteo.com/v1/archive (`models=era5`) | Tägliche Summen von Niederschlag, Regen und Schneefall → Monatssummen, Mittel über 4–6 Stützpunkte | ERA5: Hersbach et al. 2020, doi:10.1002/qj.3803 |
| GeoNames cities15000 | https://download.geonames.org/export/dump/ | Städte ≥ 100 000 Einwohner (Indikator „nahe Stadt“) | CC BY 4.0 |

**CSN-Zenodo-Katalog (ab v0.1.0 eingebunden).** Der Datensatz heißt „Chilean Seismic Catalogue – 1982 – mid-2020“, Autoren
Potin, Aden-Antoniow & Ruiz, veröffentlicht 2024-07-31. Er ist nicht versioniert. Konzept-DOI 10.5281/zenodo.11360589.

- **Abdeckung:** 1982 bis 2020-07. Im Jahr 2000 fehlen fast alle Ereignisse (148 in der Box).
- **Räumlich:** Er reicht nur bis 45,98° S, **Patagonien ist also nicht abgedeckt**. Die Aysén-Box (46–43° S) hat nur 418 Ereignisse, meist 2016–2018. Sie ist unbrauchbar und wird nicht als Region geführt. Patagonien bleibt damit ohne brauchbaren Katalog (ComCat: 81 declusterte Ereignisse).
- **Hinweis:** Die README im Zip nennt den DOI 10.5281/zenodo.13146119. Er löst nicht auf (HTTP 404, geprüft 2026-10-10). Richtig ist der Record-DOI 10.5281/zenodo.13146436.
- **Verwendung:** Weil der Katalog Mitte 2020 endet, läuft die Region `Central_Andes_CSN_ctrl` nur in `glacial-sensitivity extensions` (1990–2019). Sie fließt nicht in F1/F2-BH, Kritikalität, Power oder C1 ein.

## Abdeckung (aus `results/regions_meta.csv`)

| Region | Gruppe | Quelle | Ereignisse | Mc_ref | ≥ Mc | declustert | Mc 1990er → 2020er |
|---|---|---|---|---|---|---|---|
| SE_Alaska_AK | Gebirge | AEC | 29 727 | 2,1 | 11 513 | 5 314 | 2,0 → 1,8 |
| Alps_SED | Gebirge | SED | 12 044 | 2,1 | 2 163 | 1 335 | 2,1 → 1,3 |
| NZ_Southern_Alps | Gebirge | GeoNet | 48 856 | 2,8 | 12 486 | 4 405 | 2,7 → 2,1 |
| Iceland_Vatnajokull_IMO | Gebirge | IMO SIL | 78 804 | 2,5 | 5 866 | 1 344 | 2,6 → 0,8 |
| Greenland_GEUS | Eisschild | GEUS | 8 747 | 2,7 | 898 | 531 | (vor ~2008 kaum Daten) → 1,9 |
| Interior_AK_ctrl | Kontrolle | AEC | 43 596 | 2,1 | 14 023 | 7 234 | 2,0 → 1,7 |
| N_Switzerland_ctrl | Kontrolle | SED | 3 789 | 2,3 | 488 | 316 | 2,3 → 1,3 |
| NZ_Wellington_ctrl | Kontrolle | GeoNet | 92 011 | 2,7 | 15 415 | 10 693 | 2,4 → 1,8 |
| SE_Alaska / Alps / Patagonia / Himalaya_Karakoram / Iceland / Greenland | Gebirge/Eisschild | ComCat M ≥ 3 | 1 977 / 2 974 / 258 / 5 446 / 930 / 221 | 3,4 / 4,3 / 4,8 / 4,7 / 4,7 / 4,6 | | 477 / 161 / 81 / 584 / 44 / 42 | |
| West_Antarctica | Eisschild | ComCat | 3 | – | – | – | **nicht nutzbar** |
| Philippines, Indonesia, Japan, Central_America, Central_Andes | Kontrolle | ComCat | 11 630–66 237 | 4,6–5,0 | | 2 221–5 814 | |

**Hinweise:**
- **Mc_ref** ist das 90-%-Quantil der jährlichen MAXC+0,2-Schätzungen 1990–2025. Damit ist es konservativ für die ganze Periode.
- **Netzverdichtung:** Die Abnahme von Mc bei IMO, SED und GEUS zeigt sie deutlich. Die Jahres-Fixed-Effects in F1/F2 absorbieren solche Stufen.
- **Saisonale Detektion:** Ein Artefakt bleibt möglich, wenn Mc *saisonal* schwankt; siehe `results/seasonal_mc_by_month.csv`. SE-Alaska (AEC) hat im Dezember Mc 2,2 bei Mc_ref 2,1. Eine Unterzählung im Dezember würde den Novemberpeak eher *schwächen*. GEUS hat im November Mc 2,4.
- **Westantarktis:** In ComCat stehen nur 3 Ereignisse in der Box (1997–2015). Eine statistische Analyse ist unmöglich; die Eisschild-Gruppe besteht faktisch nur aus Grönland.
