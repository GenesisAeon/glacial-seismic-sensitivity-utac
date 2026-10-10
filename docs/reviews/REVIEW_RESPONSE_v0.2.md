# Antwort auf die Reviews zu PR #1 (v0.2-dev) – Stand 2026-10-10

Reviews (Rohfassungen liegen bei J. Römer, nicht im Repo):

| Kürzel | Review | Umfang |
|---|---|---|
| DR | „Deep-Research-Review“ (wissenschaftliche Begutachtung, deutsch; Modell nicht bekannt) | ETAS, H2.1, H2.2, Gezeiten, Lag, C2 |
| GR | Grok – Präregistrierungs-Gegenprüfung (2 Seiten) | Zeitstempel, Hashes, C2-Vollständigkeit, Kennzeichnung, Zenodo |
| CC | Claude Code – Code-Review (unvollständig, Sitzung abgebrochen) | CI, Lint, Tests unter Windows |
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
Präregistrierung berühren würde, steht als **Entwurf** in
[`../PREREG_v0.2_NACHTRAG_ENTWURF_2026-10-10.md`](../PREREG_v0.2_NACHTRAG_ENTWURF_2026-10-10.md)
(E1–E8) zur Entscheidung durch J. Römer.

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
| 14 | SE-Faktor 1,25 bei C2 mehrdeutig | DR | berechtigt (bestätigt) | benchmarks-Text korrigiert; Test pinnt Implementierung = JSON-Formel; Nullsimulation; **Entscheidung E2** |
| 15 | Baseline (Mittel log µ_y) vs. Fenster (log gepoolter MLE) asymmetrisch, Versatz ≈ 0,052 | DR | berechtigt (nachgerechnet; Simulation: mittleres D 0,045) | **Entscheidung E3** |
| 16 | σ_y²/T setzt unabhängige Jahre voraus; Schätzrauschen doppelt gezählt | DR | teilweise | E4; durch simulationskalibrierte Variante (E2c) abgedeckt |
| 17 | Kovarianz Gletscher/Kontrolle = 0 | DR | teilweise (für gemeinsame Effekte konservativ) | E4 |
| 18 | C2 ist bedingt auf eingefrorene Auslöserparameter, nicht modellunabhängig | DR | berechtigt | LIMITATIONS |
| 19 | 0,01 + 0,04 garantiert α ≤ 0,05 (Bonferroni) | DR | bestätigt | keine |
| 20 | Präreg.-Commit fa4a077 (12:50:44Z = 14:50:44 MESZ) vor Ergebnis-Commit 250457c; Baselines dazwischen | GR | bestätigt (nachgeprüft) | keine |
| 21 | Hashes konsistent, v0.1.0-Dateien byte-identisch zu Tag v0.1.0 | GR | bestätigt | keine |
| 22 | Rest-Freiheitsgrade C2: Numerik `mu_window_mle`, Katalogrevisionen, Vorlauf-Ereignisse, Software-Versionen, M6/M7-Code | GR | berechtigt | **E5/E6** (Vorschläge) |
| 23 | H2/H3 korrekt als retrospektiv, Explorativ klar getrennt | GR | bestätigt | keine |
| 24 | Zenodo: Release v0.2.0 mit Präreg.-Dateien vor 2027-01-01 | GR | berechtigt | **Entscheidung J. Römer** (kein Release durch mich) |
| 25 | CI grün, ruff/mypy sauber; 3 lokale Testfehler unter Windows = CRLF auf gehashten JSON | CC | berechtigt | `.gitattributes`: `results/frozen_*.json -text` |
| 26 | `window_ratio()` halboffen → Kalibrierung verglich 2008–2018 vs. 2020–2024 | CX | **berechtigt (bestätigt)** | Skripte korrigiert, Kalibrierung neu (`calibration_study_v2.csv`): 90-%-Obergrenze ≈ 1,30 statt 1,25; H2.1 bleibt abgelehnt (z 2,82), keine H2.2-Klasse ändert sich; Regressionstest; **Erratum E1** |
| 27 | Love-Zahlen: IERS 2010 h = 0,6078, l = 0,0847 bevorzugen | GE | teilweise (Werte geprüft; Herkunft „Farrell 1972“ nicht prüfbar) | Konstanten `LOVE_*_IERS2010`, Test (nur Skalierung, Phasen identisch); eingefrorene H3-Werte bleiben (**E7**) |
| 28 | „Kumazawa & Ogata Jahresbins“ nicht treu | GE | berechtigt (geprüft: µ(t) und K0(t) glatt, ABIC, Bruchpunkte) | Docstring und METHODS: „angelehnt an, keine Nachimplementierung“ |
| 29 | Sasgen: Island-Werte und Ensemble-Spannen „nicht gefunden“ | GE | nicht berechtigt | Stehen in Sasgen et al. 2026 (Fig. 3, Methods „Earth model parameters“, Discussion: Island 1e18 Pa·s/30 km, GNSS 40 km; Ensemble 1e18–3e19 Pa·s, 30–90 km) |
| 30 | Tanaka 2002, Tan 2019, Ogata–Katsura 1993, GK/van Stiphout 2012, IPCC AR6 A.1.7 | GE | bestätigt | keine |
| 31 | ETAS-Likelihood/Gradient (Kern bei tmax, Vorlauf nur als Auslöser, Bins) | GB | korrekt | siehe unten |
| 32 | Kovarianz bei `fix_trig` | GB | korrekt als bedingte Kovarianz | Hinweis (enthält Random-Walk-Strafterm → eher kleinere SE; durch max(OLS, Likelihood) × Faktor abgefangen) |
| 33 | Simulator: p = 1 exakt → Division durch null in der inversen CDF | GB | Fehler (klein; reale Fits nutzen p ≥ 1,0001) | behoben (log-gleichverteilte Form), Test |
| 34 | Simulator: Magnituden kontinuierlich simuliert, dann auf 0,1 gerundet und bei Mc gekappt | GB | kleine Inkonsistenz | dokumentiert, nicht geändert (würde die Wiedergewinnungsläufe verschieben; Wirkung ≈ α·0,05 auf die Produktivität) |

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
  (Abweichung zur unbeschränkten Verzweigungsformel vernachlässigbar). Randeffekt: Die
  Kalibrier-/Wiedergewinnungskataloge beginnen ohne Vorlauf und werden ohne Vorlauf angepasst –
  konsistent, keine Verzerrung von µ.

## Was offen bleibt / Entscheidungen für J. Römer

1. **E2** SE-Faktor bei C2 (ohne / × 1,25 / simulationskalibriert) – Empfehlung: simulationskalibriert.
2. **E3** symmetrisches µ_ref (neue Baseline-Datei mit neuem Hash) – Empfehlung: ja.
3. **E5/E6** Betriebsregeln für C2 (Kataloghomogenität, Archivierung, Software-Stand).
4. **E1** Erratum zum Faktor 1,25 mit v0.2.0 veröffentlichen (Wert bleibt).
5. **E7** Love-Zahlen: H3 bleibt; ggf. IERS für M7 ab 2027.
6. Release v0.2.0 + Zenodo **vor 2027-01-01** (inkl. eines angenommenen Nachtrags).
7. Rohfassungen der Reviews: nicht committet (Entscheidung, ob sie unter `docs/reviews/` sollen).
