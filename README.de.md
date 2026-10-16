# glacial-seismic-sensitivity-utac

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23281090.svg)](https://doi.org/10.5281/zenodo.23281090)

GenesisAeon-Paket **133** (Registerklasse KLIMA-KRYO-13) – Begleitpaket zu
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
| A Kippszenarien (v0.1.0) | Beschleunigte Eisverluste nach publizierten Spannen (Edwards 2021, DeConto 2021). Seismizität geförderter Störungen 2100: Grönland SO 1,0–1,24×, Amundsen (DeConto 3 °C) 1,1–1,9×, SE-Alaska 1,05–2,35×. Ein Anstieg wird frühestens 2046 nachweisbar (SE-Alaska, steilster Pfad, κ = 1); Grönland erst nach 2100. Die Abnahme der Saisonmodulation bleibt bis 2100 unter der Nachweisgrenze. |
| B Trügerische Ruhe vor dem Kippen | Im Modell möglich, wenn > 50 % der Störungen im Spannungsschatten liegen. Sie beginnt 7–60 Jahre nach Beginn der Beschleunigung, ist 4–16 % tief und frühestens ~2083 statistisch erkennbar. Die geodätischen Indikatoren reagieren früher. |
| Heutige Vorläufer M1–M5 | GRACE: nur Patagonien beschleunigt (ξ = 0,039 ± 0,007/a), Grönland und Vatnajökull verlangsamen sich. GNSS: TOMO/BACK (Amundsen), AB50 (SE-Alaska) und KELY (W-Grönland) zeigen beschleunigte Hebung. Ruhe nach der Vorab-Regel nur in den NZ-Südalpen (Kontrolle im selben Netz ähnlich). Island: keine Ruhe. |
| CSN Chile (Potin et al. 2024) | Kontrolle 1990–2019: keine wachsende Saisonmodulation (−0,070 ± 0,041 pro Jahrzehnt). Der Katalog deckt Patagonien nicht ab. |

**Was ausgeschlossen ist und was offen bleibt:** [docs/LIMITATIONS.md](docs/LIMITATIONS.md). Kurz: Ein
starker Anstieg der saisonalen Empfindlichkeit kleiner Beben seit 1990 ist in SE-Alaska
unwahrscheinlich. Verzögerte viskose Antworten, einzelne große Brüche und vulkanische Effekte sind
*nicht* ausgeschlossen.

## v0.2.1 (veröffentlicht am 2026-10-16)

Neu: Preprint [paper/P133_preprint.pdf](paper/P133_preprint.pdf) (nicht begutachtet) und eine explorative globale Basislinie ([docs/BASELINE_GLOBAL.md](docs/BASELINE_GLOBAL.md)). Keine eingefrorene Datei und kein präregistriertes Ergebnis wurde geändert.

## v0.2.0 (veröffentlicht am 2026-10-10)

Präregistrierte Ergänzung [PREREGISTRATION_v0.2.md](PREREGISTRATION_v0.2.md) (eingefroren am
2026-10-10, vor den Auswertungen; v0.1.0 unverändert). Details: [docs/RESULTS.md](docs/RESULTS.md)
(Abschnitt v0.2), [docs/METHODS_v02.md](docs/METHODS_v02.md), [docs/v02_benchmarks.md](docs/v02_benchmarks.md).
Gültiger Nachtrag [PREREGISTRATION_v0.2_NACHTRAG.md](PREREGISTRATION_v0.2_NACHTRAG.md) (2026-10-10; eingefrorene JSON
`results/frozen_v02_addendum_2026-10-10.json`, SHA-256 `bc2d2af3…7ff49`; nur Klarstellungen, frühere
eingefrorene Dateien unverändert). Rohfassungen der Reviews: [docs/reviews/raw/](docs/reviews/raw/).
Aufruf: `glacial-sensitivity v02` (Stufen m0 m1 m2 m3 m4 base plot; wiederaufnehmbar).

**Explorative globale Basislinie** (nicht präregistriert): globale M6+/M7+-Trends, vergletscherte
Regionen vs. Kontrollen, GVP-Eruptionszahlen, aus archivierten Katalog-Snapshots:
[docs/BASELINE_GLOBAL.md](docs/BASELINE_GLOBAL.md) (Englisch), `python scripts/global_baseline.py`, `results/global/`.

| Meilenstein | Ergebnis |
|---|---|
| M2 ETAS mit Jahres-Hintergrund (H2.1) | SE-Alaska minus Inner-Alaska: +0,41 ± 0,14 pro Jahrzehnt, p = 0,0017 – formal signifikant, aber getragen von 1995–2002 (niedrige Katalogzahlen in beiden Regionen); ab 2003 +0,11 ± 0,16 (explorativ). Vorab-Regel ausgelöst, aber nicht robust (ab 2003; tmax 3 a): am ehesten Katalog-/Modellartefakt, kein Gletschersignal. µ ist der ETAS-*Residual*-Hintergrund, keine identifizierte Forcing-Rate. |
| M2 trügerische Ruhe (H2.2) | Keine Region erfüllt das vorab definierte Kriterium „maskierter Hintergrundanstieg“ (moderate Effekte, v. a. Island/Grönland, nicht ausgeschlossen). Die v0.1.0-Ruhe der NZ-Südalpen ist im Modell eine echte Abnahme, aber Mc-abhängig und netzweit. |
| M3 Körpergezeit (H3) | Keine signifikante Korrelation mit der Phase der Grad-2-Körpergezeiten-Flächendehnung, kein b-Wert-Effekt (BH). SE-Alaska-MDE 6,8 % relativ zu dieser Phase. Explorative Ozeanauflast (SPOTL/TPXO 7.2), gegen Zufallszeiten getestet: weiterhin nichts signifikant (kleinstes BH-q 0,38). Störungsflächen-Spannung nicht modelliert. |
| M1 Katalog-Robustheit | F1 in SE-Alaska robust gegenüber der Entclusterung; die NZ-Ruhe verschwindet mit EMR-artigem Mc. |
| M4 Lag (Dünnplatten-/Halbraum-Sensitivität, angelehnt an Sasgen et al. 2026) | SE-Alaska frühestes Nachweisjahr 2045,8 → 2047,3 (im reduzierten Modell kaum viskositätsabhängig – Modelleigenschaft); Island τ ~300 → ~10 a, 2070 → 2062. |
| C2 (prospektiv, ab 2027-01-01) | Hintergrundänderung Gletscher vs. Kontrolle mit eingefrorenen ETAS-Parametern; Blicke 2029-12-31 (α 0,01) und 2036-12-31 (α 0,04). Baselines in `results/frozen_v02_baselines.json`. |

## Schnellstart

```bash
pip install -e ".[dev]"
glacial-sensitivity info          # Regionen, Pfade
glacial-sensitivity fetch         # ~200 MB Rohdaten nach data/raw/ (nicht im Git), ~15–30 min
glacial-sensitivity run           # alle Analysen -> results/ (~30 min)
glacial-sensitivity extensions    # Vorläufer, Kippszenarien, Quieszenz, CSN Chile (~10 min, nach run)
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
| `src/glacial_seismic_sensitivity_utac/` | `fetch/` (Daten), `catalog`, `decluster`, `glm`, `loads`, `sensitivity` (F1–F3), `lagmodel` (F5), `seasonal`, `power`, `criticality`, `confirmatory`, `precursors`, `tipping`, `quiescence`, `extensions`, `honesty`, `plots`, `cli` |
| `results/` | alle Ergebnistabellen, `frozen_confirmatory_parameters.json`, `frozen_monitoring_indicators.json` |
| `charts/` | 19 Charts (01–17) |
| `PREREGISTRATION.md` | Versuchsreihe und Präregistrierung |
| `docs/` | `METHODS`, `RESULTS`, `LAG_MODEL`, `ANALOGIES`, `DATA`, `LIMITATIONS`, `SOURCES`, `RELEASE_CHECKLIST` |
| `scripts/verify_dois.py` | prüft alle DOIs aus `constants.py` und `docs/SOURCES.md` über Crossref/DataCite |

## Ehrlichkeitsschicht

`honesty.py` enthält Funktionen, die absichtlich `False` liefern, z. B.
`does_flat_trend_exclude_delayed_response()` oder
`are_retrospective_1990_2025_tests_preregistered()`. Sie halten fest, was dieses Paket **nicht** zeigt.

## Zitieren und Lizenz

Siehe [CITATION.cff](CITATION.cff). Zenodo: v0.2.1 (with preprint) doi:10.5281/zenodo.23407045; v0.2.0 doi:10.5281/zenodo.23286492; v0.1.0 doi:10.5281/zenodo.23281091; alle Versionen (Konzept-DOI) doi:10.5281/zenodo.23281090. MIT-Lizenz. Die Daten unterliegen den Bedingungen der Anbieter
([docs/DATA.md](docs/DATA.md)). Paket 133 ist im GenesisAeon-Register als KLIMA-KRYO-13
eingetragen.
