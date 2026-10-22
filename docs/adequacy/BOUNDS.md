# AP8 – Frozen ETAS-Parameter vs. Fit-Grenzen (deskriptiv)

**Status:** deskriptiv. Diese Tabelle ändert weder die eingefrorenen Baselines noch das
C2-Verfahren noch die C2-Entscheidung. Es wird nichts neu gefittet.

- **Quelle der Werte:** `results/frozen_v02_baselines.json`
  (SHA-256 `e2fc568c93622c97607c122c210ed5fcccace0d2440b8cd420fddd931be9f401`, geprüft über
  `etas_adequacy.load_baselines`), Stage-1-Triggerparameter (stationäres ETAS, `fit_two_stage`).
- **Quelle der Grenzen:** `src/glacial_seismic_sensitivity_utac/etas_nonstat.py:268`
  `BOUNDS_TRIG = [(None, None), (0.0, 3.0), (log 1e-6, log 0.5), (1.0001, 2.5)]` für
  (log K, alpha, log c [Jahre], p), angewendet in `fit_nonstationary` (`etas_nonstat.py:322`,
  L-BFGS-B, Zeile 331–333).
  - **K:** unbeschränkt (log K ohne Grenze).
  - **alpha:** [0, 3].
  - **c_yr:** [1e-6, 0,5] Jahre (≈ 32 s bis ≈ 183 d).
  - **p:** [1,0001, 2,5].
  - **n_br:** keine Fit-Grenze, abgeleitet über `etas_nonstat.branching_ratio` mit b = 1
    (Default von `fit_nonstationary`), nur informativ.
- **Spalten:**
  - **abs. dist.:** |Wert − nächste Grenze|.
  - **rel. dist.:** abs. dist. / |Grenze|. Bei Grenze 0 ist der Wert n/a.
  - **Flag:**
    - **AT:** Abstand < 1e-6 der Boxbreite.
    - **NEAR:** Abstand < 5 % der Boxbreite. Bei c wird die Breite in log10 gemessen.
    - **ok:** sonst.
- **Regenerieren:** `python scripts/ap8_bounds_table.py --write`. Das Skript ist deterministisch
  und liest nur die JSON-Datei und `BOUNDS_TRIG`.

<!-- AP8-TABLE-BEGIN -->
| Region | Param | Value | Bound (nearest) | abs. dist. | rel. dist. | Flag |
|---|---|---:|---|---:|---:|---|
| SE_Alaska_AK | K | 0.0453566 | none (unbounded) | - | - | - |
| SE_Alaska_AK | alpha | 1.03391 | 0 (lower) | 1.03 | n/a (bound 0) | ok |
| SE_Alaska_AK | c_yr | 3.69027e-05 | 1e-06 (lower) | 3.59e-05 | 35.9 | ok |
| SE_Alaska_AK | p | 1.0001 | 1.0001 (lower) | 0 | 0 | **AT** |
| SE_Alaska_AK | n_br (derived, b=1) | 0.8407 | none (not a fit bound) | - | - | - |
| Interior_AK_ctrl | K | 0.0273989 | none (unbounded) | - | - | - |
| Interior_AK_ctrl | alpha | 1.37348 | 0 (lower) | 1.37 | n/a (bound 0) | ok |
| Interior_AK_ctrl | c_yr | 8.03351e-05 | 1e-06 (lower) | 7.93e-05 | 79.3 | ok |
| Interior_AK_ctrl | p | 1.0001 | 1.0001 (lower) | 0 | 0 | **AT** |
| Interior_AK_ctrl | n_br (derived, b=1) | 0.6406 | none (not a fit bound) | - | - | - |
| NZ_Southern_Alps | K | 0.0247946 | none (unbounded) | - | - | - |
| NZ_Southern_Alps | alpha | 1.66022 | 3 (upper) | 1.34 | 0.447 | ok |
| NZ_Southern_Alps | c_yr | 5.47156e-05 | 1e-06 (lower) | 5.37e-05 | 53.7 | ok |
| NZ_Southern_Alps | p | 1.0001 | 1.0001 (lower) | 0 | 0 | **AT** |
| NZ_Southern_Alps | n_br (derived, b=1) | 0.8726 | none (not a fit bound) | - | - | - |
| NZ_Wellington_ctrl | K | 0.0226556 | none (unbounded) | - | - | - |
| NZ_Wellington_ctrl | alpha | 1.38935 | 0 (lower) | 1.39 | n/a (bound 0) | ok |
| NZ_Wellington_ctrl | c_yr | 1.99764e-05 | 1e-06 (lower) | 1.9e-05 | 19 | ok |
| NZ_Wellington_ctrl | p | 1.0001 | 1.0001 (lower) | 0 | 0 | **AT** |
| NZ_Wellington_ctrl | n_br (derived, b=1) | 0.6185 | none (not a fit bound) | - | - | - |
| Alps_SED | K | 0.0393215 | none (unbounded) | - | - | - |
| Alps_SED | alpha | 0.839266 | 0 (lower) | 0.839 | n/a (bound 0) | ok |
| Alps_SED | c_yr | 5.27083e-05 | 1e-06 (lower) | 5.17e-05 | 51.7 | ok |
| Alps_SED | p | 1.0001 | 1.0001 (lower) | 0 | 0 | **AT** |
| Alps_SED | n_br (derived, b=1) | 0.6098 | none (not a fit bound) | - | - | - |
| N_Switzerland_ctrl | K | 0.00994346 | none (unbounded) | - | - | - |
| N_Switzerland_ctrl | alpha | 1.17462 | 0 (lower) | 1.17 | n/a (bound 0) | ok |
| N_Switzerland_ctrl | c_yr | 8.71982e-06 | 1e-06 (lower) | 7.72e-06 | 7.72 | ok |
| N_Switzerland_ctrl | p | 1.0001 | 1.0001 (lower) | 0 | 0 | **AT** |
| N_Switzerland_ctrl | n_br (derived, b=1) | 0.2366 | none (not a fit bound) | - | - | - |
| Iceland_Vatnajokull_IMO | K | 0.0453766 | none (unbounded) | - | - | - |
| Iceland_Vatnajokull_IMO | alpha | 0.0186622 | 0 (lower) | 0.0187 | n/a (bound 0) | **NEAR** |
| Iceland_Vatnajokull_IMO | c_yr | 3.07427e-06 | 1e-06 (lower) | 2.07e-06 | 2.07 | ok |
| Iceland_Vatnajokull_IMO | p | 1.06455 | 1.0001 (lower) | 0.0644 | 0.0644 | **NEAR** |
| Iceland_Vatnajokull_IMO | n_br (derived, b=1) | 0.8993 | none (not a fit bound) | - | - | - |
| Greenland_GEUS | K | 0.0880568 | none (unbounded) | - | - | - |
| Greenland_GEUS | alpha | 0.361311 | 0 (lower) | 0.361 | n/a (bound 0) | ok |
| Greenland_GEUS | c_yr | 0.000202415 | 1e-06 (lower) | 0.000201 | 201 | ok |
| Greenland_GEUS | p | 1.0001 | 1.0001 (lower) | 0 | 0 | **AT** |
| Greenland_GEUS | n_br (derived, b=1) | 0.8887 | none (not a fit bound) | - | - | - |
<!-- AP8-TABLE-END -->

## Randfälle (deskriptiv)

- **p an der Untergrenze 1,0001 in 7 von 8 Regionen.** Betroffen sind alle außer
  Iceland_Vatnajokull_IMO. Das Stage-1-Optimum liegt also auf dem Rand der Box. Das war bereits
  bekannt (`scripts/v02_review_sims.py`, `scripts/v02_stage1_propagation.py`: „boundary optimum
  p = 1.0001“).
  - Folge 1: Die Normalapproximation der Stage-1-Unsicherheit ist dort nicht gültig.
  - Folge 2: Der Omori-Schwanz ist innerhalb von tmax = 1 Jahr sehr lang. Ein p ≤ 1 ist durch
    die Box ausgeschlossen.
- **Iceland_Vatnajokull_IMO** ist nicht am Rand, aber nahe:
  - alpha = 0,019 liegt nahe der Untergrenze 0. Die Magnitudenabhängigkeit der Produktivität
    ist damit praktisch null.
  - p = 1,065 ist NEAR zur Untergrenze.
- **c, K und n_br:** c liegt überall deutlich im Inneren (≥ 2× Untergrenze). K ist
  unbeschränkt. n_br liegt zwischen 0,24 und 0,90, also überall < 1.
- **Keine Auswirkung auf C2:** Die eingefrorenen Werte bleiben, wie sie sind. Dies ist eine
  Dokumentation der Adäquatheit (vgl. Szenario `p12` in `etas_adequacy/gate_sim.py`) und kein
  Änderungs- oder Umentscheidungsgrund.
