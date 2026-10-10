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
`scripts/v02_calibration_study.py` (korrigiert, Produktionsgeometrie), `scripts/v02_calibration_summary.py`,
`scripts/v02_stage1_propagation.py`, `scripts/v02_m3_window20.py`; Ergebnisse in
`results/v02/review_sims_*.csv`, `calibration_study_v2.csv`, `calibration_prod_p*.csv`,
`calibration_summary.csv`, `stage1_propagation_*.csv`, `m3_tides_window20.csv`.
Zusätzlich verwendet: Kontrollrechnungen aus dem Code-Review von Claude Code (Rohdaten bei
J. Römer, nicht im Repo; die Kalibrierzahlen wurden hier mit Claudes Auswerteskript nachvollzogen).

## E1 – Erratum: Nullkalibrierung des Faktors 1,25 (Codex P2, Claude Code B1; bestätigt)

* **Befund (Codex, Claude Code unabhängig):** `scripts/v02_calibration_study.py` (und
  `v02_recovery_study.py`) übergaben (2008, 2019)/(2020, 2025) an `window_ratio()`, das halboffene
  Fenster nutzt → verglichen wurden 2008–2018 vs. 2020–2024. Claude Code fand zusätzlich die
  abweichende Geometrie: Kalibrierkataloge 1995–2025 (30 statt 31 Bins) ohne 5-a-Vorlauf. Der
  echte H2-Lauf (`v02.py`) nutzte die richtigen Fenster und die richtige Geometrie.
* **Korrektur:** Das Skript übernimmt jetzt FIT_T0/FIT_T1/HISTORY_YEARS/TMAX/WIN_A/WIN_B direkt aus
  `v02` (Regressionstest `tests/test_v02_scripts.py`); simuliert wird mit dem korrigierten
  Magnituden-Simulator (K2, siehe unten).
* **Ergebnisse** (stationäre Kataloge, zweistufiger Schätzer, σ_rw = 1; sd(z) ohne Faktor,
  Bootstrap-90-%-Obergrenze in Klammern):

| Lauf | Quelle | n | wahres p | sd(z) Trend | sd(z) Fensterverhältnis | p̂ an Untergrenze |
|---|---|---|---|---|---|---|
| ursprünglich (Fenster falsch, ohne Vorlauf) | v0.2-Lauf | 40 | 1,15 | 1,05 (1,17) | 1,12 (1,26) | – |
| ursprüngliche Basis 40 + 8 (nachgerechnet) | Claude Code | 48 | 1,15 | 1,11 | 1,18 | – |
| nur Fenster korrigiert | Grok Bot | 48 | 1,15 | 0,93 (1,04) | 1,13 (1,30) | – |
| produktionsgetreu | Claude Code | 48 | 1,15 | 1,11 (1,22) | 1,21 (1,35) | 4 % |
| produktionsgetreu | Claude Code | 48 | 1,02 | 1,02 (1,14) | 1,30 (1,42) | 27 % |
| produktionsgetreu, K2-Simulator | Grok Bot | 48 | 1,15 | 1,07 (1,22) | 1,24 (1,35) | 4 % |
| produktionsgetreu, K2-Simulator | Grok Bot | 48 | 1,02 | 0,96 (1,07) | 1,18 (1,27) | 29 % |

  (p̂ an Untergrenze: Anteil p̂ ≤ 1,001. Mit wahrem p = 1,02 – nahe dem Randregime der echten
  Daten – landet ein großer Teil der Schätzungen an der Untergrenze, wie in 7/8 Regionen.)
* **Lesart:** Für den Trend (H2.1) ist 1,25 ausreichend (sd(z) ≤ 1,11, Obergrenzen ≤ 1,22). Für
  das Fensterverhältnis (H2.2) wäre nach der ursprünglichen Regel („90-%-Obergrenze“) ein Faktor
  ≈ 1,3–1,4 nötig; die Punktschätzungen liegen bei 1,18–1,30.
* **Folgen** (nur Neuskalierung der SE, eingefrorene Ergebnisse aus `m2_etas_background.csv`,
  `m2_H21_did.csv`):
  * H2.1 Primärpaar: z = 2,93 (Faktor 1,25) → 2,82 (1,30) → 2,58 (1,42); p einseitig
    ≤ 0,005, BH ≤ 0,015 → **weiterhin abgelehnt**; die beiden anderen Paare bleiben nicht
    signifikant.
  * H2.2: Eine Klasse würde erst ab einem Faktor **1,56** kippen (SE-Alaska „Anstieg“ → „keine
    auflösbare Änderung“), danach 1,81 (NZ Südalpen „Abnahme“), 2,05 (N-Schweiz). Unterhalb von 1,56
    ändert sich **keine** veröffentlichte Klassifikation.
* **Empfehlung:** Der eingefrorene Wert 1,25 bleibt (keine Änderung nach Sicht der Daten). Diese
  Notiz wird als Erratum mit v0.2.0 veröffentlicht; die H2.2-Konfidenzintervalle sind als
  „eher etwas zu eng (Faktor ≈ 1,2–1,4 statt 1,25)“ zu lesen. Dank an Codex (Fund der Fenster) und
  Claude Code (Geometrie, produktionsgetreue Kalibrierung, Kipp-Schwellen).

## E2 – Mehrdeutigkeit des SE-Faktors bei C2 (Deep-Research-Review, bestätigt)

* Präregistrierung Abschnitt 2 heißt „Modell und Schätzer (H2, C2)“ und nennt SE × 1,25;
  Abschnitt 5, die JSON-Formel `C2.se` und `confirmatory_v02.region_change` enthalten **keinen**
  Faktor. `docs/v02_benchmarks.md` sprach fälschlich von „allen H2-/C2-Standardfehlern“
  (korrigiert). Der Faktor wurde aus H2-Statistiken gewonnen, nicht für C2. Implementiert ist und
  bleibt die JSON-Formel (Test pinnt das).
* Nullsimulationen der **eingefrorenen** C2-Prozedur (Alaska-ähnliche eingefrorene Parameter,
  Baseline 2016–2025, nichts ändert sich nach 2026):

| Quelle | Szenario | n | Blick | mittleres D | sd(z) | Ablehnungen (nominal) |
|---|---|---|---|---|---|---|
| Claude Code | reines ETAS | 300 | 2030 | +0,016 ± 0,012 | 0,76 | 0,3 % (1 %) |
| Claude Code | reines ETAS | 300 | 2037 | −0,000 | 0,90 | 2,3 % (4 %) |
| Claude Code | Jahresstreuung (σ 0,33 / 0,14) | 300 | 2030 | −0,022 ± 0,016 | 0,95 | 1,0 % (1 %) |
| Claude Code | Jahresstreuung (σ 0,33 / 0,14) | 300 | 2037 | −0,027 ± 0,011 | 1,05 | 3,0 % (4 %) |
| Grok Bot | Jahresstreuung (σ 0,30 / 0,12) | 100 | 2030 | +0,045 ± 0,032 | 1,11 | 2 % (1 %) |

  (± = Standardfehler des Mittels. Der kleinere Grok-Bot-Lauf ist mit Claudes größerem Lauf
  verträglich; sein positives mittleres D ist nicht signifikant.)
* **Lesart:** Die Formel ohne Faktor hält ihr Niveau ungefähr oder ist konservativ; ein
  systematischer Versatz von D ist nicht erkennbar. Bei einzelnen Szenarien liegt sd(z) leicht
  über 1 (bis 1,11), die Ablehnungsraten liegen aber innerhalb der Binomialunsicherheit am
  Nominalwert. Das M6-Flag (z ≥ 2) war in meinem Lauf unter H0 bei 5 % (nominal ≈ 2 %; n = 100).
* Optionen: (a) wie JSON, ohne Faktor; (b) × 1,25 (konservativer); (c) kritischer Wert aus einer
  größeren Nullsimulation genau dieser Prozedur (≥ 500 Läufe), vor 2027 eingefroren.
  **Empfehlung (geändert nach Claude-Code-Simulation): (a) beibehalten, die Mehrdeutigkeit per
  Nachtrag klarstellen („C2 ohne Faktor, wie JSON“).** (c) bleibt eine Option, falls J. Römer eine
  weitere Absicherung will.
* **Blickdaten (Claude Code W2, behoben ohne Regeländerung):** `evaluate_pair` erkannte die Blicke
  nur bei exakt 2030.0/2037.0; ein anderes Format (2029.997, „2029-12-31“) ergab stillschweigend
  α = NaN. Jetzt `resolve_look()`: akzeptiert das exklusive Ende (Dezimaljahr, Toleranz 0,01 a)
  und ISO-Datum des letzten Tages oder des Folgetages; alles andere wirft einen Fehler
  (ungeplante Blicke nur explizit mit `allow_unplanned=True`, dann ohne Testentscheidung). Die
  eingefrorenen Blicke und α-Werte sind unverändert.

## E3 – Symmetrie des C2-Estimanden (Deep-Research-Review, teilweise)

* Baseline = Mittel jährlicher log µ_y (geometrisch), Fenster = log eines gepoolten µ-MLE
  (≈ arithmetisch). Bei rein log-normaler Jahresstreuung wäre ein Versatz
  ½(0,358² − 0,155²) ≈ 0,052 zugunsten von D > 0 zu erwarten (Rechnung des Reviews, nachgeprüft).
* **Simulationen zeigen diesen Versatz nicht** (E2: Claude Code −0,022 ± 0,016 bzw.
  −0,027 ± 0,011 mit Jahresstreuung; Grok Bot +0,045 ± 0,032, n. s.). Die Ursache (z. B.
  gegenläufige Verzerrung der Jahres-MLE bei kleinen Zahlen) ist nicht geklärt.
* Vorschlag: µ_ref als konstanter µ-MLE über 2016–2025 mit den eingefrorenen Auslöserparametern
  (`mu_window_mle`, dasselbe Funktional wie im Fenster) – erfordert eine **neue** Baseline-Datei
  mit neuem Hash. **Empfehlung (abgeschwächt): optional, nur der Lesbarkeit/Symmetrie wegen; kein
  nachgewiesener Bias.**

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

## E9 – Suchfenster der Gezeitenphase (Claude Code K1)

* Das ±14-h-Suchfenster ist ein Code-Standardwert, nicht Teil der eingefrorenen Präregistrierung
  (dort nur die Tanaka-Konvention). Bei ±14 h bleiben 0,8–2,6 % der Beben ohne Phase; ±20 h lässt
  keine Lücken; das 5-min-Raster ist ausreichend (Claude Code: 99-%-Fehler < 1,8°).
* Explorativer Neulauf mit ±20 h: keine H3-Aussage ändert sich (kleinstes BH-q 0,10 → 0,12).
* **Empfehlung:** Für M7 ab 2027 ±20 h per Nachtrag festschreiben (zusammen mit E7).

## E10 – Unsicherheit der Stufe 1 (Claude Code W3)

* Die SE der Jahres-µ sind bedingt auf die Stufe-1-Parameter (K, α, c, p). Für H2 ist das durch
  den SE-Faktor abgedeckt, für C2 sind die Parameter eingefroren (C2 ist ausdrücklich bedingt).
* Explorative Fortpflanzung (`scripts/v02_stage1_propagation.py`, 30 Ziehungen je Region aus der
  Normalapproximation der Stufe 1, Stufe 2 neu angepasst): SE der Trends +1,0 % (SE-Alaska) bzw.
  +0,7 % (Inner-Alaska), Fensterverhältnis ≤ +2,3 %; H2.1-z 2,93 → 2,90. Normalapproximation an der
  p-Untergrenze unzuverlässig (Claude Code: Stufe 1 in Testkatalogen schlecht bestimmt).
  **Keine Änderung der eingefrorenen Prozedur; kein Nachtrag nötig.**
