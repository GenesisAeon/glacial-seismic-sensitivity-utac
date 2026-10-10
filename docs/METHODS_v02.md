# Methoden v0.2 (M0–M4)

Ergänzt [`METHODS.md`](METHODS.md). Präregistrierte Regeln: [`../PREREGISTRATION_v0.2.md`](../PREREGISTRATION_v0.2.md).
Code: `etas_nonstat.py` (M2), `tides.py` (M3), `robustness_mc.py` (M1), `lag_sensitivity.py` (M4),
`confirmatory_v02.py` (C2), Orchestrierung `v02.py` (`glacial-sensitivity v02 [stages]`,
wiederaufnehmbar, Prüfpunkte je Region in `results/v02/*_regions/`).

**Ideengeber:** Ein Gemini-Deep-Research-Bericht (2026-10-10) regte M2–M4 an. Er ist keine Quelle;
alle Zahlen hier stammen aus den zitierten Originalarbeiten oder aus eigenen Rechnungen.

## M1 – Katalog-Robustheit

* **EMR-artiges Mc** nach Ogata & Katsura 1993 (GJI 113:727, https://doi.org/10.1111/j.1365-246X.1993.tb04663.x):
  f(m) ∝ 10^(−bm)·Φ((m−µ)/σ) über alle Magnituden (gebinnte Likelihood), Mc := µ + 2σ.
  Referenz-Mc nach derselben Regel wie v0.1.0 (90-%-Quantil der Jahreswerte).
* **Bootstrap** (200×) von Mc (MAXC+0,2 und EMR) für 2008–2025.
* **Gardner-Knopoff-Fenster** (Gardner & Knopoff 1974, BSSA 64:1363) in der Form von van Stiphout,
  Zhuang & Marsan 2012 (CORSSA, https://doi.org/10.5078/corssa-52382934):
  L = 10^(0,1238M+0,983) km; T = 10^(0,032M+2,7389) d für M ≥ 6,5, sonst 10^(0,5409M−0,547) d;
  Abarbeitung nach absteigender Magnitude, Vor- und Nachbeben im Fenster werden entfernt.
* Neu gerechnet: F1 (β1, Permutationstest mit 500 statt 2000 Permutationen) und Habermann-z
  (2020–25 vs. 2008–19) mit (a) v0.1.0, (b) GK-Entclusterung, (c) EMR-Mc + NN-Entclusterung.

## M2 – ETAS mit zeitlich veränderlichem Hintergrund

λ(t) = µ_y(t) + Σ K·e^{α(m_j−Mc)}·(t−t_j+c)^{−p}, Kern bei tmax = 1 a abgeschnitten, ein µ je
Kalenderjahr 1995–2025, Ereignisse 1990–1994 nur als Auslöser. Idee: nichtstationäres ETAS
(Kumazawa & Ogata 2013, https://doi.org/10.1002/2013JB010259), hier in der einfachsten Form.
Likelihood mit analytischem Gradienten (geprüft gegen finite Differenzen), Paarsummen blockweise.
Schätzer und Kalibrierung: [`v02_benchmarks.md`](v02_benchmarks.md). Konsistenzprüfung: mit einem
einzigen Bin ist das Ergebnis identisch mit dem stationären ETAS aus v0.1.0 (`quiescence.fit_etas`).

Grenzen: rein zeitlich (kein Raumkern); bei abgeschnittenem Kern landet p in fast allen Regionen
an der Untergrenze 1,0001 (siehe RESULTS); Schwärme (Island) passen schlecht zu ETAS (α ≈ 0);
Netzänderungen verschieben µ_y direkt – deshalb nur netzinterne Gletscher-Kontroll-Differenzen.

## M3 – Körpergezeit

* Ephemeride: Hauptterme aus Meeus, *Astronomical Algorithms*, 2. Aufl. (Kap. 25 Sonne, Kap. 47 Mond);
  Test gegen Beispiel 47.a (Mond, 1992-04-12) und 25.a (Sonne, 1992-10-13): Abweichung < 0,01° bzw.
  < 30 km.
* Grad-2-Potential W2 = Σ GM·a²/r³·P2(cos ψ); Flächendehnung an der Oberfläche (2h − 6l)·W2/(g·a),
  h = 0,6114, l = 0,0832 (Herkunft noch zu belegen; die Nominalwerte der IERS Conventions 2010,
  h = 0,6078, l = 0,0847, ergeben 2 % weniger Dehnung und **identische Phasen** – Schuster-Test und
  b-Wert-Aufteilung hängen nicht davon ab). Typisch 20 nstrain (Median), 31 nstrain (95-%-Quantil) an den
  Bebenorten – grob 1–3 kPa (E = 70 GPa, ν = 0,25). Dominante Periode am Äquator 12,42 h (M2);
  in hohen Breiten überwiegt der eintägige Anteil.
* Phase nach Tanaka, Ohtake & Sato 2002 (JGR 107(B10):2211, https://doi.org/10.1029/2001JB001577),
  für jedes Beben am eigenen Ort (±14 h, 5-min-Raster).
* Schuster-Test; b-Wert-Vergleich Dehnungs- vs. Kompressionshälfte (Richtung wie Tan et al. 2019,
  EPSL 512:39, https://doi.org/10.1016/j.epsl.2019.01.047). Power per Simulation.
* **Ozeanauflast fehlt.** Für SE-Alaska, Neuseeland, Island und Grönland kann die Auflastgezeit
  größer sein als die Körpergezeit und eine andere Phase haben (Modellierung z. B. mit SPOTL wäre
  der nächste Schritt). Ein Nullbefund ist daher nur ein Nullbefund für die Körpergezeit.

## M4 – Lag-Modell mit Sasgen et al. 2026

Sasgen et al. 2026, Commun. Earth Environ. 7:518, https://doi.org/10.1038/s43247-026-03738-y:
Alaska, tomographisch bevorzugt, Asthenosphärenviskosität 3×10¹⁸ Pa·s, Lithosphärendicke 30 km;
Island 1×10¹⁸ Pa·s, 30 km (GNSS-Anpassung 40 km); Ensemble 1×10¹⁸–3×10¹⁹ Pa·s, 30–90 km.
Die Werte stehen in `lag_sensitivity.SENSITIVITY_RHEOLOGIES`; `lagmodel.RHEOLOGIES` (v0.1.0)
bleibt unverändert. Die Lithosphärendicke eines GIA-Modells wird hier als elastische Dicke Te des
Plattenfilters verwendet – eine Vereinfachung. η-Scan 10¹⁸–10²⁰ Pa·s für Te = 30 und 60 km.

## Meeresspiegel als Last (Notiz)

Der mittlere globale Meeresspiegelanstieg von 3,7 mm/a (2006–2018; IPCC AR6 WG I, SPM A.1.7,
https://www.ipcc.ch/report/ar6/wg1/chapter/summary-for-policymakers/) entspricht einer Auflast von
ρ·g·h ≈ 1025 · 9,81 · 0,0037 ≈ **37 Pa/a** – ein bis zwei Größenordnungen kleiner als die
Entlastung über schrumpfenden Gletschern (GRACE-Boxen v0.1.0: 0,4 kPa/a Patagonien, 0,9–1,9 kPa/a sonst). Sie wird nicht
modelliert.

## „2046“ – Klarstellung

Die Zahl 2046 (genauer 2045,8) aus v0.1.0 ist das **früheste Nachweisjahr** eines Ratenanstiegs
im günstigsten Szenario für SE-Alaska (Oberflächenlast, κ = 1), **kein Höhepunkt** und keine
Vorhersage eines Ereignisses.

## English summary

M1 re-runs F1 and Habermann z with an Ogata–Katsura (EMR-type) Mc, Mc bootstrap and
Gardner–Knopoff declustering. M2 is a temporal ETAS with yearly background (two-stage estimator,
tmax 1 yr). M3 computes the degree-2 body-tide areal strain (own Meeus ephemeris, validated) and
Tanaka phases; ocean loading is not included. M4 re-runs the v0.1.0 lag model with the
Sasgen et al. (2026) viscosities without changing the v0.1.0 values. Sea-level rise adds ~37 Pa/yr
load (not modelled). "2046" is the earliest detection year in the most favourable v0.1.0 scenario,
not a peak.
