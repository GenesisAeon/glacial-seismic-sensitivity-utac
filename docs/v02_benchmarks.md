# v0.2 – M0 Benchmark und synthetische Prüfung des ETAS-Hintergrundmodells

Alle Zahlen aus `results/v02/m0_benchmark.csv`, `recovery_study_v2.csv` (vorher `recovery_study.csv`), `calibration_study.csv` / `calibration_prod_p*.csv`
(reproduzierbar mit `glacial-sensitivity v02 m0` bzw. `scripts/v02_recovery_study.py`,
`scripts/v02_calibration_study.py`). Gemeinsam genutzte Maschine, ~3 GB freier Arbeitsspeicher.

## M0 – Paare, Laufzeit, Speicher (keine Anpassung)

Ereignisse ≥ Mc 1990–2025 (fünf Jahre Vorlauf vor 1995), ein Likelihood-plus-Gradient-Aufruf:

| Region | Ereignisse | Paare tmax 1 a | 3 a | 5 a | Spitze RAM 1 a | 5 a | Likelihood+Gradient 1 a |
|---|---|---|---|---|---|---|---|
| SE_Alaska_AK | 10 046 | 5,4 Mio. | 10,3 Mio. | 15,0 Mio. | 0,26 GB | 0,74 GB | 0,19 s |
| Interior_AK_ctrl | 13 727 | 14,9 Mio. | 25,1 Mio. | 33,7 Mio. | 0,73 GB | 1,65 GB | 0,49 s |
| NZ_Southern_Alps | 12 341 | 9,3 Mio. | 17,4 Mio. | 24,3 Mio. | 0,46 GB | 1,19 GB | 0,31 s |
| NZ_Wellington_ctrl | 15 239 | 7,0 Mio. | 19,4 Mio. | 31,3 Mio. | 0,34 GB | 1,53 GB | 0,24 s |
| Iceland_Vatnajokull_IMO | 5 810 | 6,8 Mio. | 8,2 Mio. | 9,4 Mio. | 0,33 GB | 0,46 GB | 0,26 s |
| Alps_SED | 2 128 | 0,15 Mio. | 0,41 Mio. | 0,67 Mio. | < 0,04 GB | | 0,005 s |
| Greenland_GEUS / N_Switzerland_ctrl | 852 / 471 | < 0,05 Mio. | | | < 0,01 GB | | < 0,01 s |

**Entscheidung:** tmax = 1 Jahr (wie v0.1.0). 5 Jahre wären bis 1,65 GB je Region – auf der geteilten
Maschine zu knapp für parallele Läufe. tmax = 3 Jahre läuft als explorative Prüfung nur für das
Primärpaar (`results/v02/m2_exploratory_robustness.csv`).

## Synthetische Wiedergewinnung (8 Kataloge je Szenario, 1995–2025)

Wahre Auslöserparameter K = 0,0276, α = 1,0, c = 0,002 a, p = 1,15 (Verzweigungsverhältnis ≈ 0,5).
Szenarien: konstant 80/a; linear 50→100/a; „maskierter Anstieg“ (60/a, ab 2015 exponentiell steigend,
M7 im Jahr 2010).

| Szenario | Schätzer | p (wahr 1,15) | Verzw. (≈0,5) | µ-Fehler | Trend/Jahrzehnt (wahr) | sd(z) |
|---|---|---|---|---|---|---|
| konstant | gemeinsam, σ_rw 1 | 1,83 | 0,33 | +28 % | 0,006 (0) | 1,29 |
| konstant | gemeinsam, σ_rw 0,2 | 1,70 | 0,36 | +24 % | 0,005 (0) | 1,46 |
| konstant | **zweistufig** | 1,16 | 0,53 | −6 % | −0,000 (0) | 1,11 |
| linear | gemeinsam, σ_rw 1 | 1,78 | 0,32 | +28 % | 0,237 (0,227) | 1,28 |
| linear | **zweistufig** | 1,02 | 0,70 | −35 % | 0,210 (0,227) | 0,61 |
| maskiert | gemeinsam, σ_rw 1 | 1,48 | 0,38 | +19 % | 0,137 (0,130) | 1,04 |
| maskiert | **zweistufig** | 1,05 | 0,61 | −22 % | 0,120 (0,130) | 0,89 |

*Neu gerechnet am 2026-10-10* (`recovery_study_v2.csv`) mit dem korrigierten Magnituden-Simulator
(Review K2) und den Produktionsfenstern für das Verhältnis (E1). Die ursprünglichen Zahlen
(`recovery_study.csv`, alter Simulator) waren qualitativ gleich: gemeinsamer Schätzer p 1,48–1,70,
Verzweigung 0,33–0,36, sd(z) 1,10–1,87; zweistufig p 1,03–1,16, sd(z) 0,80–1,42. Die Lesart
unten gilt unverändert.

Lesart: Mit freien Jahres-µ verschiebt der gemeinsame Schätzer den langen Omori-Schwanz in den
Hintergrund (p zu hoch, Verzweigung zu klein) und unterschätzt die Unsicherheit des Trends. Der
zweistufige Schätzer liefert den Trend leicht abgeschwächt (konservativ) und besser kalibrierte
Fehler; das **Niveau** von µ ist bei steigendem Hintergrund verzerrt (die stationäre Stufe 1
schreibt einen Teil des Anstiegs der Auslösung zu). Für H2/C2 zählen nur Trends und Verhältnisse.

## Nullkalibrierung (40 + 8 stationäre Kataloge)

Zweistufig, σ_rw = 1: sd(Trend) = 0,034 bei mittlerem SE 0,032 (40 Kataloge); zusammen mit den
8 Katalogen der Wiedergewinnung sd(z) = 1,11 (Trend) und 1,18 (Fensterverhältnis), Bootstrap-
90-%-Obergrenze ≈ 1,25. Daher der vorab festgelegte Faktor 1,25 auf die H2-Standardfehler
(Trend und Fensterverhältnis). *Korrektur 2026-10-10:* Die frühere Formulierung „auf alle
H2-/C2-Standardfehler“ war falsch; die eingefrorene C2-Formel (JSON, Präregistrierung Abschnitt 5,
`confirmatory_v02.py`) enthält den Faktor nicht. Die Mehrdeutigkeit mit Abschnitt 2 der
Präregistrierung ist im Nachtragsentwurf `PREREG_v0.2_NACHTRAG_BEGRUENDUNG_2026-10-10.md` gelistet.

**Erratum 2026-10-10 (Codex-Review zu PR #1; Claude-Code-Review B1).**
`scripts/v02_calibration_study.py` und `v02_recovery_study.py` übergaben die H2.2-Fenster als
(2008, 2019)/(2020, 2025); `window_ratio()` nimmt halboffene Fenster, verglichen wurden also
2008–2018 mit 2020–2024; außerdem endeten die Kalibrierkataloge 2025,0 (30 statt 31 Jahresbins) und
hatten keinen Vorlauf. Der echte Lauf (`v02.py`, WIN_A/WIN_B) war korrekt. Das Kalibrierskript
übernimmt jetzt die Produktionsgeometrie direkt aus `v02` (1995–2026, 5 a Vorlauf, tmax 1 a,
WIN_A/WIN_B; Regressionstest `tests/test_v02_scripts.py`). Produktionsgetreu (je 48 Kataloge):
sd(z) Trend 0,96–1,07, Fensterverhältnis 1,18–1,24 (90-%-Obergrenzen bis 1,35; Claude Code mit
eigenem Lauf: bis 1,42). Für den Trend (H2.1) reicht 1,25; für das Fensterverhältnis wären
≈ 1,2–1,3 nötig. Keine veröffentlichte Klassifikation ändert sich unterhalb eines Faktors 1,56.
Zahlen und Folgen: Nachtragsentwurf, E1. Der Faktor 1,25 bleibt als eingefrorener Wert
unverändert.
Ohne Strafterm (σ_rw = 100) ändern sich die Zahlen kaum (sd 0,034).

## English summary

M0: with tmax = 1 yr the largest region needs 0.73 GB and 0.5 s per likelihood+gradient
evaluation; tmax = 5 yr would need up to 1.65 GB, so tmax = 1 yr was kept (as v0.1.0). Synthetic
recovery: the joint MLE with free yearly background trades the Omori tail against the bin rates
(p too high, branching ratio too low, SEs too small); the two-stage estimator (stationary
triggering parameters, then yearly mu) gives slightly attenuated, better-calibrated trends. Null
calibration gives sd(z) ≈ 1.1–1.2, hence the preregistered SE factor 1.25.
