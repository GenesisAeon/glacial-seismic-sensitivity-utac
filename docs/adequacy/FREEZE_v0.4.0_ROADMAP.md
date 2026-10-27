# Freeze v0.4.0: Roadmap (Paket 0)

Stand 2026-10-26, Branch `v0.4.0-freeze` von `main` = `225883c`. Frist im Kalender 2026-11-16, harte Grenze 2026-12-31 (vor jedem Datum des Prüffensters 2027-01-01).
Plan vom 2026-10-23 (Johann: v0.4.0 = Einfrier-Schritt für A8 + A9). **Jeder Schritt mit Johanns Freigabe; nichts wird gepusht, getaggt oder veröffentlicht ohne seine Zeile.**

## Ausgangslage (geprüft)
- A8-Text: `docs/adequacy/A8_addendum_draft.md` (ENTWURF; enthält Gate L+T3, Seed- und Fensterregel, Referenzstichprobe, Probeläufe 2023–2025 und 2036, Addendum B = 10.000 vom 2026-10-25).
- A9-Text: `docs/adequacy/A9_c2_zone_confirmation_draft.md` mit `results/adequacy/c2_zone_spec.json` (Status DRAFT).
- T3-Statistik: `etas_adequacy/stats.py`, `m_test_ks2` (Zeile ~134). Kein Schutz gegen Float-Darstellungsunterschiede bei gebinnten Magnituden (Befund aus dem Probelauf 2036, `a8_dryrun_2036_projection.md`).
- Eingefrorene Dateien und Prüfsummen: `etas_adequacy/frozen.py` (Baselines `e2fc568c…`, b-Werte `404fc555…`), `results/frozen_v02_*.json`, `results/frozen_v03_preregistration.json`.
- Muster für ein datiertes Addendum: `results/frozen_v02_addendum_2026-10-10.json` + `PREREGISTRATION_v0.2_NACHTRAG.md` + Tests in `tests/test_v02_prereg.py`.

## Pakete (je ein Commit, volle Regression vor jedem Commit)
| Nr. | Inhalt | Abnahme |
|---|---|---|
| F0 | diese Roadmap | — |
| F1 | **Code-Absicherung T3:** `m_test_ks2` rundet beide Stichproben auf 6 Nachkommastellen, bevor getestet wird. Test, der am alten Code fehlschlägt (gleiche Verteilung in zwei Float-Darstellungen → alter p-Wert winzig, neuer p = 1). Bestehende Pins müssen unverändert bleiben (echte Daten haben dieselbe Darstellung). | Tests grün, Pins unverändert |
| F2 | **A8-Text fertigstellen:** drei Ergänzungen aus Claudes Prüfung vom 2026-10-25 (Reproduzierbarkeit B = 500 vs. 10.000; gemessene 6,7 h auf der Run-Box statt Hochrechnung, Laufzeit hardwareabhängig; echte Auswertung nur mit dem fortsetzbaren Bootstrap); Verweis auf den T3-Guard aus F1. Kennzeichnung bleibt ENTWURF bis F4. | Claude-Prüfung, dann **Johann liest** |
| F3 | **A9 einfrieren vorbereiten:** `c2_zone_spec.json` von DRAFT auf FROZEN mit Datum; Text A9 final. | **Johann entscheidet** (Inhalt war am 2026-10-23 beschlossen: Bestätigung ohne 55-km-Zone, Regel A) |
| F4 | **Zweiter Nachtrag** (`PREREGISTRATION_v0.2_NACHTRAG_2.md`, Text aus A8 + A9) + **Addendum-JSON** `results/frozen_v04_addendum_<Datum>.json` mit SHA-256 aller eingefrorenen Dateien (Baselines, b-Werte, `c2_zone_spec.json`, Snapshot 2026, Nachtrag-Dokument, A8/A9-Texte) + Tests nach dem Muster von `test_v02_prereg.py` (Hashes stimmen, Schlüsselentscheidungen gepinnt). | **Johanns Freigabe des Wortlauts** |
| F5 | Version 0.4.0, CHANGELOG, README-Abschnitt | CI grün |
| F6 | Push des Branches, PR, Merge, **Tag v0.4.0, Release, Zenodo** | **Johanns Push-Freigabe und Merge-Anweisung** |

## Nicht in diesem Freeze
Keine neuen Analysen, keine Änderung an den eingefrorenen v0.2-Dateien, kein Blick auf Daten ab 2027.
