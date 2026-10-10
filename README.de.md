# glacial-seismic-sensitivity-utac

GenesisAeon-Paket **133 (provisorisch)** – Begleitpaket zu
[`glacial-seismicity-utac`](https://github.com/GenesisAeon/glacial-seismicity-utac) (P101).
Geprüft wird, ob Erdbebenkataloge nahe schmelzender Gletscher ein **Frühstadium** einer verzögerten
Reaktion auf Eisentlastung zeigen – nicht über Ratentrends, sondern über eine wachsende
**Empfindlichkeit** gegenüber der saisonalen Last. **Bewusst ohne UTAC/CREP/AFET-Brücke** – siehe
[DISCLAIMER.md](DISCLAIMER.md).

*English version: [README.md](README.md). Allgemeinverständlich: [WHITEPAPER.md](WHITEPAPER.md).*

## Fragestellung

Reagiert der Erdmantel verzögert (Jahrzehnte bis Jahrtausende), ist ein heute flacher Trend der
Bebenraten keine Entwarnung. Empfindlicher ist die Frage, ob *dieselbe* saisonale Entlastung im
Lauf der Zeit *mehr* Beben auslöst. Das Paket testet das mit echten Katalogen (USGS ComCat, Alaska
Earthquake Center, Schweizerischer Erdbebendienst, GeoNet, Veðurstofa Íslands, GEUS), GRACE-Lasten
und ERA5-Niederschlag. Ein konfirmatorischer Test auf Daten ab **November 2026** ist präregistriert.

## Wichtigste Ergebnisse (Daten 1990–2025; Details in [docs/RESULTS.md](docs/RESULTS.md))

| Test | Ergebnis |
|---|---|
| F1 wachsende Saisonmodulation | Nach Benjamini-Hochberg in keiner Region signifikant. SE-Alaska (AEC, primär): +0,035 ± 0,023 pro Jahrzehnt, einseitiges Permutations-p = 0,10. Island: *abnehmend*. Grönland: p = 0,006 unkorrigiert, vermutlich Netzartefakt. |
| F2 Empfindlichkeit pro kPa (GRACE) | SE-Alaska: 4,0 ± 1,1 % pro kPa saisonaler Entlastung (nahe Johnson et al. 2020: 3,5 %/kPa), aber **kein Wachstum** (−1,3 ± 1,1 % pro kPa und Jahrzehnt). |
| F3 Regen vs. Last | SE-Alaska: nicht trennbar (r = 0,68). Neuseeland, Südalpen: Last besser als Regen (explorativ). |
| Lag-Modell (Szenarien) | Relaxationszeiten von 23 Jahren (Patagonien) bis ~2000 Jahren (Alpen). Schmale Gebirgslasten wirken überwiegend elastisch. Ein verzögerter viskoser Ratenanstieg wäre in keinem von 126 Szenarien vor ~2155 als Trend nachweisbar. |
| Kritikalitäts-Batterie | 16 von 544 Einzeltests nach BH signifikant, überwiegend Netz-/Mc-, b-Wert- und Varianzeffekte (4 in Kontrollregionen); 0 von 180 Gruppenvergleichen Gletscher vs. Kontrolle; nirgends steigende Autokorrelation. |
| Konfirmatorischer Test C1 | Eingefroren am 2026-10-10. Looks 2029-10-31 (α 0,01) und 2036-10-31 (α 0,04). Bis 2036 erkennbar: etwa eine Verdopplung der SE-Alaska-Modulation. |

**Was ausgeschlossen ist und was offen bleibt:** [docs/LIMITATIONS.md](docs/LIMITATIONS.md). Kurz: Ein
starker Anstieg der saisonalen Empfindlichkeit kleiner Beben seit 1990 ist in SE-Alaska
unwahrscheinlich. Verzögerte viskose Antworten, einzelne große Brüche und vulkanische Effekte sind
*nicht* ausgeschlossen.

## Schnellstart

```bash
pip install -e ".[dev]"
glacial-sensitivity info          # Regionen, Pfade
glacial-sensitivity fetch         # ~200 MB Rohdaten nach data/raw/ (nicht im Git), ~15–30 min
glacial-sensitivity run           # alle Analysen -> results/ (~30 min)
glacial-sensitivity plot          # Charts -> charts/
glacial-sensitivity lag           # GIA-Relaxationszeiten (ohne Daten)
pytest                            # Offline-Tests mit synthetischen Daten und Fixtures
```

Konfirmatorischer Lauf (nach 2029-10-31 + 30 Tage):

```bash
GSS_END=2029-12-01 glacial-sensitivity fetch --force
python -m glacial_seismic_sensitivity_utac.confirmatory 2029-10-31
```

## Aufbau

| Pfad | Inhalt |
|---|---|
| `src/glacial_seismic_sensitivity_utac/` | `fetch/` (Daten), `catalog`, `decluster`, `glm`, `loads`, `sensitivity` (F1–F3), `lagmodel` (F5), `seasonal`, `power`, `criticality`, `confirmatory`, `honesty`, `plots`, `cli` |
| `results/` | alle Ergebnistabellen, `frozen_confirmatory_parameters.json` |
| `charts/` | 15 Charts (01–13) |
| `PREREGISTRATION.md` | Versuchsreihe und Präregistrierung |
| `docs/` | `METHODS`, `RESULTS`, `LAG_MODEL`, `ANALOGIES`, `DATA`, `LIMITATIONS`, `SOURCES`, `RELEASE_CHECKLIST` |
| `scripts/verify_dois.py` | prüft alle DOIs aus `constants.py` über Crossref |

## Ehrlichkeitsschicht

`honesty.py` enthält Funktionen, die absichtlich `False` liefern, z. B.
`does_flat_trend_exclude_delayed_response()` oder
`are_retrospective_1990_2025_tests_preregistered()`. Sie halten fest, was dieses Paket **nicht** zeigt.

## Zitieren und Lizenz

Siehe [CITATION.cff](CITATION.cff). MIT-Lizenz. Die Daten unterliegen den Bedingungen der Anbieter
([docs/DATA.md](docs/DATA.md)). Die Paketnummer 133 ist provisorisch, bis sie im GenesisAeon-Register
eingetragen ist.
