# Nachtrag zur Präregistrierung v0.2 – in Kraft ab 2026-10-10 (P133, KLIMA-KRYO-13)

**Status:** in Kraft gesetzt und eingefroren am 2026-10-10, **vor** dem Beginn des C2-Fensters
(2027-01-01) und vor jedem C2- oder M6/M7-Datum. Maschinenlesbare, verbindliche Fassung:
`results/frozen_v02_addendum_2026-10-10.json`,
SHA-256 `bc2d2af32192ae5f31312c0609ee850223f23470637350df9795ee18f6e7ff49`.
Entscheidung: J. Römer (GenesisAeon), nach der Review-Runde 1 zu PR #1. Begründung und Belege:
[`docs/PREREG_v0.2_NACHTRAG_BEGRUENDUNG_2026-10-10.md`](docs/PREREG_v0.2_NACHTRAG_BEGRUENDUNG_2026-10-10.md),
Review-Tabelle: [`docs/reviews/REVIEW_RESPONSE_v0.2.md`](docs/reviews/REVIEW_RESPONSE_v0.2.md).

Dieser Nachtrag folgt Abschnitt 8 der Präregistrierung v0.2 („jede spätere Änderung ist ein
neuer, datierter Nachtrag mit neuem Hash“). **Unverändert** bleiben (SHA-256 in der JSON-Datei,
geprüft von `tests/test_v02_prereg.py`): `PREREGISTRATION_v0.2.md`,
`results/frozen_v02_preregistration.json` (`af7a5d02…`), `results/frozen_v02_baselines.json`
(`e2fc568c…`) und die beiden v0.1.0-Dateien. Archivierung auf Zenodo mit dem Release v0.2.0,
**vor dem 2027-01-01**. Danach werden C2-Regeln nicht mehr geändert.

## A1 – C2: Standardfehler ohne Faktor (Klarstellung)

C2 nutzt die eingefrorene JSON-Formel `C2.se` **ohne** den H2-Faktor 1,25. Der Faktor in
Abschnitt 2 („Modell und Schätzer (H2, C2)“) gilt nur für die retrospektiven H2-Standardfehler,
nicht für C2 und nicht für M6. Die Statistik selbst ändert sich nicht. Beleg:
Nullsimulationen der eingefrorenen Prozedur halten das Niveau oder sind konservativ.

## A2 – C2: Referenz bleibt; symmetrisches µ_ref erwogen und verworfen

µ_ref und σ_y bleiben wie in `results/frozen_v02_baselines.json`. Erwogen wurde ein µ_ref als
konstanter µ-MLE 2016–2025, also dasselbe Funktional wie im Fenster. Das ist **verworfen**:
Die Nullsimulationen zeigen den erwarteten Jensen-Versatz (≈ 0,05) nicht. Lesbarkeit allein
rechtfertigt keine neue Baseline-Datei.

## A3 – C2: Blickdaten

Die Blick-Enden der JSON sind **inklusive** letzte Datentage (2029-12-31, 2036-12-31). Die
Datenfenster sind [2027-01-01, 2030-01-01) und [2027-01-01, 2037-01-01), als Dezimaljahre mit
exklusiven Enden 2030,0 (α = 0,01) und 2037,0 (α = 0,04). Andere Enden sind keine geplanten
Blicke; `confirmatory_v02.resolve_look` bricht dann ab.

## A4 – Betriebsregeln für C2 und M6/M7

1. **Katalog-Snapshot:**
   - Vor jeder Berechnung (Blick oder jährliche Monitoring-Prüfung) wird der Katalogauszug jeder verwendeten Region archiviert, auf Zenodo.
   - Mitarchiviert werden Abrufzeit (UTC), Abfrage-URL bzw. -Parameter und die SHA-256 der Datei.
   - Magnituden gelten „wie zum Abrufzeitpunkt“, belegt durch die archivierte Datei.
2. **Homogenität:**
   - Für jedes Fensterjahr und beide Regionen eines Paares wird das Jahres-Mc berichtet (MAXC + 0,2 und EMR, Δm 0,1).
   - Liegt einer dieser Werte in einem Fensterjahr über Mc_ref + 0,2, wird der Blick zusätzlich mit einem gemeinsamen, entsprechend erhöhten Mc gerechnet und als „Homogenität fraglich“ markiert.
   - Die Entscheidung bleibt bei der eingefrorenen Statistik mit Mc_ref.
   - Bekannte Netzänderungen werden berichtet: Stationslisten der zuliefernden Netze aus FDSN-Metadaten.
3. **Serielle Korrelation:** Mit jedem Blick wird die Lag-1-Autokorrelation der Referenzjahre (2016–2025) mitberichtet, nur beschreibend.
4. **Vorlauf-Ereignisse:**
   - Alle Beben ≥ Mc_ref in [2026-01-01, 2027-01-01) zählen nur als Auslöser.
   - Bei späteren Blicken zählen alle Ereignisse ab 2026-01-01.
5. **Numerik:** `mu_window_mle` löst mit dem Brent-Verfahren, SciPy-Standardtoleranzen, Startintervall (1e-9, n/T + 1).
6. **Software:**
   - Verbindlich ist der Code des Releases v0.2.0 (Git-Tag `v0.2.0` und seine Zenodo-DOI).
   - Python- und Paketversionen (`pip freeze`) werden mit jedem Blick archiviert.
   - Eine spätere Code-Version darf nur verwendet werden, wenn sie das v0.2.0-Ergebnis auf dem archivierten Snapshot bis auf 1e-6 in D und SE reproduziert.

## A5 – H2: Erratum E1, Faktor 1,25 bleibt

- **Faktor:** Der eingefrorene H2-Faktor 1,25 bleibt unverändert.
- **Erratum E1:** Es betrifft Fenster und Geometrie der Nullkalibrierung. Produktionsgetreu kalibriert gilt:
  - Trend: sd(z) ≤ 1,11.
  - Fensterverhältnis: sd(z) 1,18–1,30, 90-%-Obergrenzen bis 1,42.
- **Veröffentlichung:** Das Erratum erscheint mit v0.2.0. Die H2.2-Intervalle sind als etwas zu eng zu lesen.
- **Folgen:** Unterhalb eines Faktors 1,56 ändert sich keine veröffentlichte Entscheidung.

## A6 – M7 ab 2027: Gezeitenphase

- **Phase:** Tanaka-Phase der Grad-2-Körpergezeiten-Flächendehnung.
- **Love-Zahlen:** nominal nach IERS Conventions 2010, h = 0,6078 und l = 0,0847 (2h − 6l = 0,7074).
- **Gitter:** Extremum-Suche ±20 h, 5-min-Raster (`confirmatory_v02.m7_tidal_flag`).
- **Flag-Regel unverändert:** Schuster-p < 0,01 bei N ≥ 200 entclusterten Beben.
- **Ozeanauflast:** nicht Teil von M7; darf daneben beschreibend berichtet werden.
- **H3:** Das retrospektive H3 (Körpergezeit, eingefrorene Love-Zahlen, ±14 h wie gerechnet) wird nicht neu entschieden.

## A7 – Lesehinweise (ohne Wirkung auf Statistiken)

- **µ_y:** µ_y ist die ETAS-Residual-Hintergrundrate. „Statt durch sinkenden Antrieb“ in Abschnitt 4 ist zu lesen als „statt durch einen sinkenden ETAS-Residual-Hintergrund“.
- **Kumazawa & Ogata 2013:** „Idee: Kumazawa & Ogata 2013“ heißt „angelehnt an“, keine Nachimplementierung.
- **H3:** H3 testet nur die Korrelation mit der Phase der Grad-2-Körpergezeiten-Flächendehnung.
- **Stufe 1:** Die H2-SE sind bedingt auf die Stufe-1-Parameter. Die explorative Fortpflanzung ergibt +1–2 %; keine Änderung.

## English summary

Dated addendum to the v0.2 preregistration, frozen on 2026-10-10 before the C2 window opens.
Binding file: `results/frozen_v02_addendum_2026-10-10.json` (SHA-256 above). The original
v0.2 files and the v0.1.0 files are unchanged.

- **A1:** C2 uses the frozen SE formula without the H2 factor 1.25. The factor applies to H2 only.
- **A2:** The frozen μ_ref stays. A symmetric μ_ref was considered and rejected: there is no offset in the null simulations.
- **A3:** Look ends are inclusive last days, i.e. exclusive 2030.0 (α 0.01) and 2037.0 (α 0.04). Other looks are refused.
- **A4:** Operating rules:
  - archived catalogue snapshots with retrieval time and SHA-256 (Zenodo);
  - yearly Mc reporting with a flagged sensitivity run if Mc exceeds Mc_ref + 0.2;
  - reporting of network changes and of reference-period autocorrelation;
  - history-event rule and mu_window_mle numerics;
  - code pinned to release v0.2.0 with pip freeze archived.
- **A5:** H2 factor 1.25 unchanged; Erratum E1 published with v0.2.0.
- **A6:** From 2027, M7 uses IERS 2010 Love numbers (h 0.6078, l 0.0847) and a ±20 h window. Ocean loading is descriptive only. H3 is not re-decided.
- **A7:** Reading notes.
