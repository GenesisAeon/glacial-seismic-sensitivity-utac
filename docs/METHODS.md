# Methoden (Kurzfassung)

Die vollständige Spezifikation der Hypothesentests steht in [`../PREREGISTRATION.md`](../PREREGISTRATION.md).

## Pipeline

1. **Aufbereitung** (`catalog.py`):
   - Filter nach Box, Ausschlusspolygon (Grönland: Island-Sektor) und maximaler Tiefe.
   - Ereignisse ab 1990-01-01, Magnituden auf 0,1 gerundet.
2. **Vollständigkeit:** Mc pro Jahr (MAXC + 0,2); Mc_ref = 90-%-Quantil der Jahreswerte 1990–2025.
3. **Declustering** (`decluster.py`):
   - Nearest-Neighbour-Distanz η nach Zaliapin & Ben-Zion (2013), doi:10.1002/jgrb.50179, mit d_f = 1,6, b = 1.
   - Schwelle η0 aus einem 2-Komponenten-Gauß-Mix von log10 η; Fallback −5, wenn die Verteilung nicht bimodal ist.
   - Ergebnisse werden in `data/derived/` gecacht.
4. **Saisonale Modulation** (`seasonal.py`):
   - Schuster-Test (Amplitude 2R/N, p = exp(−R²/N), Phase).
   - Robustheitsvarianten nach Magnitude, Tiefe, Halbzeiten und roh vs. declustert.
   - Mc nach Kalendermonat, Klimatologie, 6-Jahres-Fenster.
   - Kantishna-Aufteilung und 1°-Phasenkarte. Johnson et al. 2020 berichten gegenläufige Phasen nördlich und südlich der Denali-Verwerfung, die sich in Regionalsummen auslöschen können.
5. **Frühstadium-Tests F1/F2/F3** (`sensitivity.py`, `glm.py`):
   - Poisson-GLM mit Jahres-Fixed-Effects (IRLS).
   - Quasi-Poisson-SE (Pearson-Dispersion φ, nie < 1).
   - Permutationstest durch Vertauschen der Jahr→τ-Zuordnung (Monate bleiben im Jahr), 2000 Permutationen.
   - Benjamini-Hochberg über Regionen.
   - Inverse-Varianz-Meta-Analyse je Gruppe und Tier.
6. **Last** (`loads.py`):
   - GSFC-Mascons (ohne Ozean-Mascons) mit Mittelpunkt in der Box, flächengewichtet.
   - 1 cm w.e. = 0,0981 kPa.
   - Saisonanomalie = Wert − zentriertes 13-Monats-Mittel; U = −Anomalie.
   - Trend und Jahresamplitude per harmonischer Regression.
7. **Niederschlag:** ERA5-Monatssummen an 4–6 festen Stützpunkten pro Region (`config.PRECIP_POINTS`), Anomalie wie bei der Last.
8. **Kritikalitäts-Batterie** (`criticality.py`, aus Phase 2 übernommen):
   - 20 Indikatoren in 2-Jahres-Bins, darunter Raten, b-Werte, Clustering, Zwischenzeit-Statistik, Saisonamplitude, Stadtnähe sowie Kontrollgrößen (Mc, Anteil mb).
   - b-Werte in 100-Ereignis-Fenstern.
   - Kendall-τ-Trend mit Block-Permutation.
   - CSD-Indikatoren (Varianz, AR1, Schiefe, Kurtosis, Erholungsrate) auf trendbereinigten Monatszahlen gegen IAAFT-Surrogate.
   - BH über alle Tests; Gruppen-Permutationstests getrennt nach Tier.
9. **Lag-Modell** (`lagmodel.py`): siehe [`LAG_MODEL.md`](LAG_MODEL.md).
10. **Power und eingefrorene Parameter** (`power.py`, `confirmatory.py`): siehe PREREGISTRATION.

## Reproduktion

```bash
pip install -e ".[dev]"
glacial-sensitivity fetch        # ~10 min, ~210 MB (davon 172 MB GRACE)
glacial-sensitivity run          # ~30 min (Kritikalitäts-Batterie mit 10 000 Permutationen / 2000 Surrogaten dominiert); --no-criticality: ~1 min
glacial-sensitivity plot
pytest                           # offline, synthetische Fixtures
```

- **Seeds:** fest (`config.SEED = 20261010`).
- **Umgebungsvariablen:** `GSS_N_PERM_SENS`, `GSS_N_SURROGATES` und `GSS_N_PERM` setzen die Zahl der Permutationen bzw. Surrogate (Standard 2000 / 2000 / 10 000; mit 500 Surrogaten und 2000 Permutationen liegt das kleinste erreichbare q bei ~0,06, deshalb die höheren Standardwerte). `GSS_RAW`, `GSS_OUT` und `GSS_CHARTS` setzen die Pfade.

## Erweiterungen (v0.1.0): `glacial-sensitivity extensions`

Der Befehl läuft nach `run`, Laufzeit ~10 min (ETAS-Fits). Er ändert keine Ergebnisse des Hauptlaufs.

- **`precursors.py`:** Kleinste-Quadrate-Fit y = a + v(t−2015) + (A/2)(t−2015)² + Jahres- und Halbjahresgang (+ Sprünge).
  - Die Fehler werden mit √((1+ρ)/(1−ρ)) aus der Lag-1-Autokorrelation ρ der Residuen inflationiert.
  - GRACE: Boxen in `config.EXTRA_GRACE_BOXES`. GNSS: 14 Stationen in `config.GNSS_STATIONS`, NGL-Sprungliste.
- **`tipping.py`:** Lastpfade m(t) mit Entlastungsrate L̇(t) = L̇_heute·m(t).
  - GIA-Spannungsrate: Ṡ_GIA = κ[(1−C)L̇ + C(L̇ ∗ e^{−t/τ}/τ)], mit τ und C aus `lagmodel`.
  - Geförderte Störungen: (Ṡ0 + Ṡ_GIA)/(Ṡ0 + Ṡ_GIA,2025).
  - Schattenstörungen: exakte Dieterich-ODE (aσ = 1,5 kPa) mit Spannungsrate Ṡ0 − Ṡ_GIA.
  - Katalog: (1−f)·gefördert + f·Schatten.
  - Nachweis: log-linearer Trend ab 2026-11 gegen `lagmodel.mde_slope`. Abnahme der Modulation wie C1 (einseitig, Faktor 2,487).
- **`quiescence.py`:** Zeitliches ETAS (μ, K, α, c, p), Maximum-Likelihood mit L-BFGS-B, Kern nach 1 Jahr abgeschnitten.
  - Fit 1995–2014.5, Erwartung im Testfenster einschließlich Triggerung durch beobachtete Ereignisse.
  - Habermann-z auf entclusterten Jahreszahlen. KS-Test der Magnituden ≥ Mc und Median des jährlichen Mc.
  - Klassifikation nach `PREREGISTRATION.md` §6.
- **`extensions.run_csn`:** F1 und Saisonalitäts-Robustheit für den CSN-Katalog, 1990–2019.
- **Eingefroren:** Schwellen und Basiswerte in `results/frozen_monitoring_indicators.json`. Diese Datei wird nie überschrieben; spätere Läufe schreiben `_RECOMPUTED`.
