# Antwort auf die Reviews zu PR #1 (v0.2-dev) – Stand 2026-10-10

Reviews (Rohfassungen liegen bei J. Römer, nicht im Repo):

| Kürzel | Review | Umfang |
|---|---|---|
| DR | „Deep-Research-Review“ (wissenschaftliche Begutachtung, deutsch; Modell nicht bekannt) | ETAS, H2.1, H2.2, Gezeiten, Lag, C2 |
| GR | Grok – Präregistrierungs-Gegenprüfung (2 Seiten) | Zeitstempel, Hashes, C2-Vollständigkeit, Kennzeichnung, Zenodo |
| CC | Claude Code – vollständiges Code-Review von decb368 (2026-10-10, mit eigenen Prüfskripten und Simulationen) | CI, Lint, Windows, ETAS-Likelihood/Gradient/Simulator, Kalibrierung, C2-Nullsimulation, Gezeitenphase, GK, Speicher |
| CX | Codex – Kommentar P2 im PR | `scripts/v02_calibration_study.py:38` |
| GE | Gemini – enge Literaturprüfung | 8 Zitate/Zahlen |
| GB | Grok Bot – Nachholen der ETAS-Prüfungen 1+2 aus `docs/REVIEW_PROMPTS.md` (CC kam nicht dazu) | Likelihood, Gradient, Kovarianz, Simulator |

Neue Literatur- und Zahlenbehauptungen wurden vor Übernahme an Primärquellen geprüft:
Sasgen et al. 2026 (https://doi.org/10.1038/s43247-026-03738-y, Methods „GIA modelling“ und
„Earth model parameters“), Kumazawa & Ogata 2013 (https://doi.org/10.1002/2013JB010259, Abschnitt
zu Glättung/ABIC), Tsuruoka, Ohtake & Sato 1995 (https://doi.org/10.1111/j.1365-246X.1995.tb03546.x,
Abstract), IERS Conventions 2010 (TN 36, Kap. 7, Gl. 7.5,
https://www.iers.org/IERS/EN/Publications/TechnicalNotes/tn36.html). Rechnungen des DR
(Omori-Massenanteil 0,79/0,65; Power-Schwellen; Versatz 0,052) wurden nachgerechnet.

**Nicht geändert:** v0.1.0-Dateien, `results/frozen_v02_preregistration.json` (`af7a5d02…`),
`results/frozen_v02_baselines.json` (`e2fc568c…`), `PREREGISTRATION_v0.2.md`. Alles, was die
Präregistrierung berührt, wurde in
[`../PREREG_v0.2_NACHTRAG_BEGRUENDUNG_2026-10-10.md`](../PREREG_v0.2_NACHTRAG_BEGRUENDUNG_2026-10-10.md)
(E1–E10) begründet; J. Römer hat am 2026-10-10 alle Empfehlungen angenommen. In Kraft ist
[`../../PREREGISTRATION_v0.2_NACHTRAG.md`](../../PREREGISTRATION_v0.2_NACHTRAG.md)
(`results/frozen_v02_addendum_2026-10-10.json`, SHA-256 `bc2d2af3…7ff49`).

## Tabelle

| # | Punkt | Rev. | Urteil | Aktion |
|---|---|---|---|---|
| 1 | µ(t) ist ETAS-Residual-Hintergrund, keine identifizierte Forcing-Rate | DR | berechtigt | Begriff in RESULTS, METHODS_v02, READMEs, LIMITATIONS, Docstring `etas_nonstat` festgelegt |
| 2 | Zweistufiger Fit defensibel, schreibt aber Produktivitäts-/Vollständigkeitsänderungen µ zu | DR | berechtigt | Estimand-Absatz in METHODS_v02 |
| 3 | p = 1,0001 in 7/8 Regionen ist ernstes Diagnosezeichen; harter Cutoff bei p ≈ 1 nicht harmlos (0,79 der 5-a-Masse im 1. Jahr) | DR | berechtigt (nachgerechnet) | RESULTS „Überraschungen“ präzisiert |
| 4 | Verzweigungsverhältnisse sind cutoff-abhängig, keine Reproduktionszahl | DR | berechtigt | Fußnote in RESULTS, LIMITATIONS |
| 5 | Recovery-Studie deckt das Randregime (p ≈ 1, hohe Verzweigung) nicht ab | DR | berechtigt | Explorative Nullsimulation im Randregime: sd(z) 0,89/0,92 (Gletscher/Kontrolle, ohne Faktor) – SE nicht zu klein |
| 6 | H2.1: Regel korrekt ausgelöst, physikalische Deutung scheitert (Netz/Katalog plausibelste Erklärung) | DR | berechtigt, inhaltlich bereits so | Fazit in RESULTS/README nach DR-Formulierung geschärft |
| 7 | Netzinterne Kontrolle schützt nicht vor differentiellen Netzänderungen | DR | bereits umgesetzt (Präreg. Abschn. 3, LIMITATIONS) | Für C2: Homogenitätsregel vorgeschlagen (E5) |
| 8 | H2.2: harte Grenze beim Gesamtverhältnis, µ- und Rohzählung abhängig; 2D-Kontrast mit Nullsimulation sauberer | DR | teilweise | Als deskriptiv gekennzeichnet (war präregistriert); 2D-Kontrast nicht umgesetzt (Kandidat für spätere Version) |
| 9 | H2.2: „criterion not met“ statt „kein masked rise“; Power-Schwellen je Region | DR | berechtigt (nachgerechnet: 1,3–2,4) | Spalte „µ-Verhältnis für 80 % Power“ und Formulierung in RESULTS/README |
| 10 | (2h − 6l)W2/(ga) korrekt; Love-Zahlen 2,3 % neben IERS | DR | bestätigt | keine (siehe 27) |
| 11 | H3 testet nur Phase der Körpergezeiten-Flächendehnung; Ozeanauflast und Störungsflächen-Spannung fehlen (Tsuruoka et al. 1995) | DR | berechtigt (Quelle geprüft) | H3 in RESULTS/METHODS/README genau benannt, MDE eingeschränkt, Tsuruoka et al. zitiert |
| 12 | Sasgen-LT ≠ Te, AV ≠ Halbraumviskosität | DR | berechtigt (VILMA, 4 Schichten, Asthenosphäre bis 400 km – geprüft) | „Dünnplatten-/Halbraum-Sensitivität, angelehnt an Sasgen et al.“ in RESULTS/METHODS/README |
| 13 | „Elastischer Anteil dominiert“ ist Modelleigenschaft; Te steuert C und τ zugleich | DR | berechtigt | Lesart in RESULTS/METHODS umformuliert |
| 14 | SE-Faktor 1,25 bei C2 mehrdeutig | DR | berechtigt (bestätigt) | benchmarks-Text korrigiert; Test pinnt Implementierung = JSON-Formel; Nullsimulationen (CC, GB): Niveau ohne Faktor gehalten; **E2**: Empfehlung jetzt „wie JSON, per Nachtrag klarstellen“ |
| 15 | Baseline (Mittel log µ_y) vs. Fenster (log gepoolter MLE) asymmetrisch, Versatz ≈ 0,052 | DR | teilweise: Rechnung stimmt für rein log-normale Streuung, in Simulationen aber kein Versatz (CC 2×300: −0,022 ± 0,016 / −0,027 ± 0,011; GB n = 100: +0,045 ± 0,032, n. s.) | **E3** abgeschwächt: symmetrisches µ_ref nur optional |
| 16 | σ_y²/T setzt unabhängige Jahre voraus; Schätzrauschen doppelt gezählt | DR | teilweise | E4; durch simulationskalibrierte Variante (E2c) abgedeckt |
| 17 | Kovarianz Gletscher/Kontrolle = 0 | DR | teilweise (für gemeinsame Effekte konservativ) | E4 |
| 18 | C2 ist bedingt auf eingefrorene Auslöserparameter, nicht modellunabhängig | DR | berechtigt | LIMITATIONS |
| 19 | 0,01 + 0,04 garantiert α ≤ 0,05 (Bonferroni) | DR | bestätigt | keine |
| 20 | Präreg.-Commit fa4a077 (12:50:44Z = 14:50:44 MESZ) vor Ergebnis-Commit 250457c; Baselines dazwischen | GR | bestätigt (nachgeprüft) | keine |
| 21 | Hashes konsistent, v0.1.0-Dateien byte-identisch zu Tag v0.1.0 | GR | bestätigt | keine |
| 22 | Rest-Freiheitsgrade C2: Numerik `mu_window_mle`, Katalogrevisionen, Vorlauf-Ereignisse, Software-Versionen, M6/M7-Code | GR | berechtigt | **E5/E6** (Vorschläge) |
| 23 | H2/H3 korrekt als retrospektiv, Explorativ klar getrennt | GR | bestätigt | keine |
| 24 | Zenodo: Release v0.2.0 mit Präreg.-Dateien vor 2027-01-01 | GR | berechtigt | **Entscheidung J. Römer** (kein Release durch mich) |
| 25 | CI grün, ruff/mypy sauber; 3 lokale Testfehler unter Windows = CRLF auf gehashten JSON | CC | berechtigt | `.gitattributes`: `results/*.json`, `results/frozen_*.json`, `PREREGISTRATION*.md` mit `-text` |
| 26 | `window_ratio()` halboffen → Kalibrierung verglich 2008–2018 vs. 2020–2024 | CX, CC (B1) | **berechtigt (bestätigt)** | Skripte nutzen jetzt die Produktionsgeometrie aus `v02` (CC: auch Vorlauf und 31. Bin fehlten); produktionsgetreue Kalibrierung (CC und GB): Trend sd(z) ≤ 1,11 → 1,25 reicht; Fensterverhältnis 1,18–1,30 (Obergrenzen bis 1,42); H2.1 bleibt abgelehnt; H2.2-Klassen kippen erst ab Faktor 1,56; Regressionstest `test_v02_scripts.py`; **Erratum E1** |
| 27 | Love-Zahlen: IERS 2010 h = 0,6078, l = 0,0847 bevorzugen | GE | teilweise (Werte geprüft; Herkunft „Farrell 1972“ nicht prüfbar; eingefrorene Werte = SPOTL-Körpergezeit, s. u.) | Konstanten `LOVE_*_IERS2010`, Test (nur Skalierung, Phasen identisch); eingefrorene H3-Werte bleiben (**E7**) |
| 28 | „Kumazawa & Ogata Jahresbins“ nicht treu | GE | berechtigt (geprüft: µ(t) und K0(t) glatt, ABIC, Bruchpunkte) | Docstring und METHODS: „angelehnt an, keine Nachimplementierung“ |
| 29 | Sasgen: Island-Werte und Ensemble-Spannen „nicht gefunden“ | GE | nicht berechtigt | Stehen in Sasgen et al. 2026 (Fig. 3, Methods „Earth model parameters“, Discussion: Island 1e18 Pa·s/30 km, GNSS 40 km; Ensemble 1e18–3e19 Pa·s, 30–90 km) |
| 30 | Tanaka 2002, Tan 2019, Ogata–Katsura 1993, GK/van Stiphout 2012, IPCC AR6 A.1.7 | GE | bestätigt | keine |
| 31 | ETAS-Likelihood/Gradient (Kern bei tmax, Vorlauf nur als Auslöser, Bins) | GB | korrekt | siehe unten |
| 32 | Kovarianz bei `fix_trig` | GB, CC (W3) | korrekt als bedingte Kovarianz (CC: = eigene Hesse-Rechnung bis 4,7e-11; Strafterm −1,4 %) | Docstring + METHODS; explorative Stufe-1-Fortpflanzung (`v02_stage1_propagation.py`, **E10**) |
| 33 | Simulator: p = 1 exakt → Division durch null in der inversen CDF | GB | Fehler (klein; reale Fits nutzen p ≥ 1,0001) | behoben (log-gleichverteilte Form), Test |
| 34 | Simulator: Magnituden kontinuierlich ab Mc, dann auf 0,1 gerundet → unterster Bin halb so breit, b ≈ 0,90 statt 1 | GB, CC (K2) | Fehler (nur Simulationen betroffen) | **behoben**: Ziehung ab Mc − Δm/2, Rundung auf das Raster (`dm`), b jetzt 0,997; Test. Produktionsgetreue Kalibrierung mit korrigiertem Simulator neu gerechnet; ältere Simulations-CSVs (Wiedergewinnung, `calibration_study*.csv`, `review_sims_*.csv`) stammen vom alten Simulator |
| 35 | W2: C2-Blicke nur bei exakt 2030.0/2037.0 erkannt, sonst stillschweigend α = NaN | CC | berechtigt | `resolve_look()` mit Toleranz/ISO-Datum, unbekannte Blicke → Fehler; Tests (E2) |
| 36 | K1: ±14-h-Suchfenster lässt 1–3 % der Beben ohne Gezeitenphase | CC | berechtigt (nachgeprüft: 0,8–2,6 %) | Explorativer Neulauf ±20 h: keine H3-Aussage ändert sich; Fenster war nicht eingefroren; **E9** (±20 h für M7); Test |
| 37 | K3: fehlende Tests (Kalibrierfenster, GK-Vorbeben/Gleichstand, Gradient an p-Untergrenze mit Vorlauf, Simulator-b) | CC | berechtigt | Tests ergänzt |
| 38 | K4: `read_text()` ohne Kodierung (cp1252 unter Windows) | CC | berechtigt | überall `encoding="utf-8"` |
| 39 | K5: CI prüft nur aktuelle Paketversionen | CC | berechtigt | CI-Job `test-min-deps` (numpy 1.26, pandas 2.1, scipy 1.11, matplotlib 3.8; lokal grün) |
| 40 | K6: Simulator bei p = 1 | CC | = Nr. 33 | bereits behoben |
| 41 | Ohne Befund: Likelihood/Kompensator vs. Quadratur (1,1e-11), Gradient vs. zentrale Differenzen (bis 5,6e-7 an p ≈ 1), Simulator-KS (p 0,80), Phasenkonvention, GK, v0.1.0 unverändert, Speicher (49 B/Paar, ≈ 0,74 GB), Lint | CC | bestätigt | keine |

## ETAS-Prüfungen 1+2 (nachgeholt, GB)

* **Likelihood:** λ an Zielereignissen = µ(Bin) + Summe über alle früheren Ereignisse innerhalb
  (0, tmax] (auch Vorlauf vor t0). Kompensator: Σ µ_b·Binlänge + Σ_j w_j·[F(t1 − t_j) − F(t0 − t_j)]
  mit F(x) = ∫₀^{min(x, tmax)}; für Vorlauf-Ereignisse zählt nur der Anteil ab t0, Ereignisse ≥ t1
  fallen heraus. Gleichzeitige Ereignisse (dt = 0) lösen einander nicht aus. Korrekt.
* **Gradient:** Ableitungen nach log K, α, log c, p analytisch nachgerechnet (inkl. ∂F/∂c,
  ∂F/∂p); Test gegen finite Differenzen vorhanden. Bei p → 1 ist ∂F/∂p numerisch unkritisch
  (Auslöschung ~1e-9 absolut).
* **Bins/Strafterm:** Bin-Zuordnung über `searchsorted`, Random-Walk-Gradient korrekt.
* **Kovarianz bei fix_trig:** Inverse der negativen Hesse-Matrix des µ-Blocks = bedingte
  Kovarianz gegeben (K, α, c, p); deren Unsicherheit ist nicht enthalten (für H2 so gewollt und
  durch Kalibrierung abgedeckt; für C2 siehe Tabelle Nr. 18).
* **Simulator:** Inverse CDF des abgeschnittenen Omori-Kerns korrekt für p ≠ 1; p = 1 behoben.
  Kinder jenseits t1 werden verworfen; Verzweigung über Generationen; GR bei m_max 8 abgeschnitten
  (Abweichung zur unbeschränkten Verzweigungsformel vernachlässigbar). Die Wiedergewinnungs-
  kataloge beginnen ohne Vorlauf und werden ohne Vorlauf angepasst (konsistent); die
  Kalibrierkataloge nutzen jetzt die Produktionsgeometrie mit 5 a Vorlauf (E1).
* **Magnituden (K2):** Siehe Nr. 34 – behoben.

## Zusammenfassung Claude-Code-Review (CC, Stand decb368)

Dank an Claude Code für ein gründliches, eigenständig nachgerechnetes Review (eigene Prüfskripte
und Simulationen; Rohfassung und Daten bei J. Römer, nicht im Repo). Kernaussagen und Umgang:

* **B1 (Blocker, mit Codex P2):** Nullkalibrierung des Faktors 1,25 mit falschen Fenstern und
  abweichender Geometrie. Bestätigt, behoben, produktionsgetreu neu gerechnet (CC und GB
  übereinstimmend): 1,25 reicht für den Trend, für das Fensterverhältnis wären ≈ 1,2–1,4 nötig;
  keine veröffentlichte Entscheidung kippt unterhalb 1,56. Erratum E1, eingefrorener Wert bleibt.
* **K0 (C2-Nullsimulation, 2×300):** kein Jensen-Versatz, Niveau gehalten oder konservativ → E2/E3
  abgeschwächt (C2 wie JSON).
* **W2** Blickdaten robust (behoben), **W3** bedingte Kovarianz bestätigt und dokumentiert,
  explorative Stufe-1-Fortpflanzung (+1 % SE), **K1** ±20 h (keine H3-Änderung), **K2** Simulator-b
  (behoben, 0,895 → 0,997), **K3** Tests ergänzt, **K4** UTF-8 + `.gitattributes`, **K5**
  CI-Mindestversionen, **K6** p = 1 (bereits behoben).
* **Ohne Befund:** Likelihood/Kompensator, Gradient (auch an der p-Untergrenze), Simulator-Verteilung,
  Phasenkonvention, Gardner–Knopoff, Unverändertheit von v0.1.0, Speicherbedarf, Lint.

## Entscheidungen (2026-10-10) und was offen bleibt

Entschieden (J. Römer, umgesetzt im Nachtrag A1–A7):

1. **E1** Erratum zum Faktor 1,25 erscheint mit v0.2.0; der Wert bleibt eingefroren (A5).
2. **E2** C2-Standardfehler ohne SE-Faktor, wie in der JSON; klargestellt (A1).
3. **E3** symmetrisches µ_ref erwogen und verworfen (A2).
4. **E5/E6** Betriebsregeln für C2: Kataloghomogenität, archivierte Katalog-Schnappschüsse mit
   SHA-256, festgelegter Software-Stand v0.2.0 (A4).
5. **E7/E9** M7 ab 2027 mit ±20-h-Fenster und IERS-2010-Love-Zahlen (A6); H3 bleibt unverändert.
   Herkunft der eingefrorenen H3-Werte h = 0,6114, l = 0,0832 geklärt: Es sind die
   Körpergezeiten-Werte von SPOTL (`loadcomb`, Agnew 1997/2012).
6. Rohfassungen der Reviews (Deep Research, Grok als PDF, Claude Code) unter
   [`raw/`](raw/); der Gemini-Bericht nicht (nur als Ideenquelle zitiert).

Explorativ bearbeitet (nicht präregistriert; Zahlen in RESULTS):

7. **Ozeanauflast (H3, Punkt 11):** SPOTL mit TPXO 7.2 (8 Partialtiden) – gegen Zufallszeiten
   getestet nichts signifikant (kleinstes BH-q 0,38); siehe RESULTS M3. Nebenbefund: Die
   Tanaka-Phase der vollen Gezeit ist zu Zufallszeiten nicht gleichverteilt.
8. **Netzänderungen (H2.1):** Stationszahlen (EarthScope-FDSN) und jährliches Mc als Kovariaten –
   der Trend wird teilweise, nicht vollständig erklärt; ein Netzartefakt ist weder belegt noch
   ausgeschlossen.
9. **Wiedergewinnungsstudie** mit korrigiertem Simulator wiederholt (`recovery_study_v2.csv`):
   qualitativ unverändert.

Offen:

10. Release v0.2.0 + Zenodo **vor 2027-01-01**.
11. Ozeanauflast im Nahfeld (Fjorde) mit feinerem Gezeitenmodell; störungsflächen-aufgelöste
    Spannung; Netzgeschichte vor ~2000 (alte AEC-Kurzperiodenstationen fehlen in FDSN-Metadaten).
