# ENTWURF – Nachtrag/Abweichungsnotiz zur Präregistrierung v0.2 (Stand 2026-10-10)

> **Status: ENTWURF, NICHT IN KRAFT, NICHT EINGEFROREN.** Diese Datei ändert weder
> `results/frozen_v02_preregistration.json` (SHA-256 `af7a5d02…d927d3`) noch
> `results/frozen_v02_baselines.json` (SHA-256 `e2fc568c…be9f401`) noch irgendeine v0.1.0-Datei.
> Sie sammelt die Punkte aus den Reviews zu PR #1, die **nur über einen datierten Nachtrag**
> (Präregistrierung Abschnitt 8) umgesetzt werden könnten, mit Belegen und Empfehlung.
> **Entscheidung: J. Römer.** Ein angenommener Nachtrag muss als eigene Datei mit eigenem
> JSON-Hash **vor dem 2027-01-01** eingefroren und (mit v0.2.0) auf Zenodo archiviert werden.
> Danach werden C2-Regeln nicht mehr geändert.

Explorative Rechnungen hierzu (nicht präregistriert): `scripts/v02_review_sims.py`,
`scripts/v02_calibration_study.py` (korrigiert), `scripts/v02_calibration_summary.py`;
Ergebnisse in `results/v02/review_sims_*.csv`, `calibration_study_v2.csv`, `calibration_summary.csv`.

## E1 – Erratum: Fenster in der Nullkalibrierung des Faktors 1,25 (Codex-Review, bestätigt)

* Befund: `scripts/v02_calibration_study.py:38` (und `v02_recovery_study.py`) übergaben
  (2008, 2019)/(2020, 2025) an `window_ratio()`, das halboffene Fenster nutzt → verglichen wurden
  2008–2018 vs. 2020–2024; zusätzlich endeten die Kalibrierkataloge 2025,0 (30 statt 31 Bins).
  Der echte H2-Lauf (`v02.py`) nutzte die richtigen Fenster.
* Korrigierter Lauf (48 stationäre Kataloge, σ_rw = 1, 1995–2025):

| Lauf | n | sd(z) Trend (90-%-Obergrenze) | sd(z) Fensterverhältnis (90-%-Obergrenze) |
|---|---|---|---|
| ursprünglich (fehlerhafte Fenster) | 40 | 1,05 (1,17) | 1,12 (1,26) |
| korrigiert | 48 | 0,93 (1,04) | 1,13 (1,30) |

  (Der ursprüngliche Wert 1,25 bezog zusätzlich 8 Wiedergewinnungskataloge ein; die Zahlen oben
  sind ohne diese, daher leicht anders als in `v02_benchmarks.md`.)
* Nach der ursprünglichen Regel („90-%-Obergrenze“) ergäbe sich **≈ 1,30** statt 1,25.
* Folgen bei Faktor 1,30 statt 1,25 (nur Neuskalierung der SE):
  * H2.1 Primärpaar: z = 2,93 → **2,82**, p einseitig 0,0024, BH 0,007 → **weiterhin
    abgelehnt**; die beiden anderen Paare bleiben nicht signifikant. Der Trend allein ist mit
    sd(z) ≈ 0,93 sogar überkalibriert, 1,25 ist dort konservativ.
  * H2.2: Keine Klasse ändert sich (geprüft für alle 8 Regionen).
* Empfehlung: Der eingefrorene Wert 1,25 bleibt (keine Änderung nach Sicht der Daten). Diese
  Notiz wird als Erratum mit v0.2.0 veröffentlicht.

## E2 – Mehrdeutigkeit des SE-Faktors bei C2 (Deep-Research-Review, bestätigt)

* Präregistrierung Abschnitt 2 heißt „Modell und Schätzer (H2, C2)“ und nennt SE × 1,25;
  Abschnitt 5, die JSON-Formel `C2.se` und `confirmatory_v02.region_change` enthalten **keinen**
  Faktor. `docs/v02_benchmarks.md` sprach fälschlich von „allen H2-/C2-Standardfehlern“
  (korrigiert). Der Faktor wurde aus H2-Statistiken gewonnen, nicht für C2.
* Explorative Nullsimulation der **eingefrorenen** C2-Prozedur (Alaska-ähnliche, eingefrorene
  Parameter: Verzweigung 0,84/0,64, p = 1,0001; wahre Jahresstreuung des Hintergrunds log-normal
  σ = 0,30 bzw. 0,12; nichts ändert sich nach 2026; Baseline 2016–2025, erster Blick 2027–2029;
  n = 100):
  * mittleres D = **0,045** (sd 0,32), mittlere SE 0,32;
  * sd(z) = **1,11** (soll 1), mittleres z 0,14;
  * Ablehnungen bei α = 0,01: **2 %** (2/100); mit SE × 1,25: 1 %;
  * M6-Flag (z ≥ 2, nur Gletscherregion) unter H0: 5 % (nominal ≈ 2 %).
  Mit n = 100 ist die Ablehnungsrate grob (2/100, Binomialunsicherheit groß). Alle Kennzahlen
  deuten aber in dieselbe Richtung: Die Formel ohne Faktor ist leicht antikonservativ (sd(z) > 1,
  M6 unter H0 zu oft), und D hat unter H0 einen kleinen positiven Versatz.
* Optionen: (a) wie JSON, ohne Faktor; (b) × 1,25; (c) Faktor bzw. kritischer Wert aus einer
  größeren Nullsimulation genau dieser Prozedur (≥ 500 Läufe), vor 2027 eingefroren.
  **Empfehlung: (c), ersatzweise (b).** Alles vor 2027-01-01 als Nachtrag mit Hash.

## E3 – Symmetrie des C2-Estimanden (Deep-Research-Review, bestätigt)

* Baseline = Mittel jährlicher log µ_y (geometrisch), Fenster = log eines gepoolten µ-MLE
  (≈ arithmetisch). Bei log-normaler Jahresstreuung gilt log E[µ] = E[log µ] + σ²/2; mit den
  eingefrorenen σ_y (0,358 / 0,155) ergibt das ½(0,358² − 0,155²) ≈ **0,052** Versatz zugunsten
  von D > 0 (Rechnung des Reviews, nachgeprüft). Die Simulation (E2) zeigt einen Versatz derselben
  Größenordnung.
* Vorschlag: µ_ref als konstanter µ-MLE über 2016–2025 mit den eingefrorenen Auslöserparametern
  (`mu_window_mle`, dasselbe Funktional wie im Fenster). Das erfordert eine **neue**
  Baseline-Datei mit neuem Hash (die alte bleibt in der Historie). Alternativ den erwarteten
  Versatz σ²/2-Differenz vorab abziehen. **Empfehlung: neues, symmetrisches µ_ref.**

## E4 – Serielle Korrelation und Abhängigkeit der Regionen (Deep-Research-Review, teilweise)

* σ_y²/T setzt unabhängige Jahre voraus; σ_y enthält zugleich Schätzrauschen, das mit se_neu²
  doppelt gezählt wird (konservativ). Die Kovarianz Gletscher/Kontrolle wird auf 0 gesetzt
  (für gemeinsame Netzeffekte konservativ). Die Hauptgefahr sind **differentielle**
  Netzänderungen (Bias, kein Varianzproblem).
* Vorschlag: durch E2 (c) mit abgedeckt; zusätzlich Autokorrelation der Baseline-Jahre berichten.

## E5 – Kataloghomogenität im C2-Fenster (Deep-Research-Review; Grok-Review)

Vorschlag für eine vorab festgelegte Betriebsregel:
* Katalogabzug zum Blickdatum mit Abrufdatum und Prüfsumme archivieren (Zenodo); Magnituden „wie
  zum Abrufzeitpunkt“ (so schon im JSON) – dokumentiert durch die archivierte Datei.
* Jahres-Mc (MAXC+0,2 und EMR) im Fenster für beide Regionen berichten; liegt eines davon in einem
  Fensterjahr über Mc_ref + 0,2, wird der Blick zusätzlich mit erhöhtem gemeinsamem Mc gerechnet
  und als „Homogenität fraglich“ markiert (Entscheidung bleibt die eingefrorene Statistik).
* Bekannte Netzänderungen (Stationslisten AK/AEC) werden berichtet.

## E6 – Restliche Freiheitsgrade (Grok-Review)

* Numerik von `mu_window_mle`: Brent-Verfahren (SciPy-Standardtoleranzen), Startintervall
  (1e-9, n/T + 1); festgeschrieben durch den Code-Stand des Releases v0.2.0 (Tag + Zenodo-DOI).
* Software: Python- und Paketversionen des Releases (Lock-Datei/`pip freeze` im Release
  archivieren).
* Vorlauf-Ereignisse: alle Beben ≥ Mc_ref in [2026-01-01, 2027-01-01) (= tmax 1 a) nur als
  Auslöser; bei späteren Blicken alle Ereignisse ab 2026-01-01.
* M6/M7: Anwendung über `confirmatory_v02.region_change` (`z_m6`) bzw. `tides.schuster`; Code
  ebenfalls über den Release-Tag fixiert.

## E7 – Love-Zahlen (Gemini-Literaturprüfung, teilweise)

* IERS Conventions 2010 (Petit & Luzum, IERS TN 36, Kap. 7, Gl. 7.5): h = 0,6078, l = 0,0847
  (geprüft). Für die präregistrierten Werte 0,6114/0,0832 wurde keine Quelle gefunden; die
  Behauptung des Gemini-Checks, sie stammten von Farrell (1972), konnte nicht geprüft werden und
  wird nicht übernommen.
* Phasen sind identisch (positiver Faktor 0,978), H3-Entscheidungen hängen nicht davon ab.
  **Empfehlung:** H3 mit den eingefrorenen Werten belassen; Amplituden zusätzlich mit
  IERS-Werten angeben; für M7 ab 2027 ggf. per Nachtrag auf IERS umstellen (ohne Wirkung auf die
  Phase).

## E8 – Formulierungen in der Präregistrierung (Deep-Research-Review)

Der eingefrorene Text bleibt unverändert. Lesehinweise:
* „statt durch sinkenden Antrieb“ (Abschnitt 4) ist als „statt durch einen sinkenden
  ETAS-Residual-Hintergrund“ zu lesen; µ ist keine identifizierte Forcing-Rate.
* „Idee: Kumazawa & Ogata 2013“ (Abschnitt 2): starke Vereinfachung, keine Nachimplementierung
  (dort µ(t) und K0(t) glatt, ABIC, Bruchpunkte).
* H3 testet die Korrelation mit der Phase der Grad-2-Körpergezeiten-Flächendehnung, nicht
  „Gezeitenauslösung“ allgemein.

## Zusätzliche explorative Prüfung: H2-Kalibrierung im Randregime

Nullsimulation mit den Alaska-ähnlichen Auslöserparametern (p = 1,0001, Verzweigung 0,84 / 0,64),
stationärer Hintergrund 1995–2025, zweistufiger Schätzer wie präregistriert (n = 20 je
Region): geschätztes p 1,0001–1,046; sd(z) des Trends Gletscher 0,89, Kontrolle 0,92
(ohne Faktor). Die H2.1-SE sind also auch im Randregime p ≈ 1 nicht zu klein; 1,25 ist dort
konservativ. (Nicht geprüft: Netzsprünge, Schwärme, räumliche Heterogenität.)
