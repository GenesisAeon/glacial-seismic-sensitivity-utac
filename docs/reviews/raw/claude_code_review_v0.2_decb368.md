# Code-Review PR #1 – glacial-seismic-sensitivity-utac v0.2 (Stand `decb368`)

**Reviewer:** Claude Code (Teil 1 von `docs/REVIEW_PROMPTS.md`). **Datum:** 2026-10-10.
**Nichts gemergt, getaggt, gepusht oder im PR kommentiert.** Review-Klon `D:/mandala/.reviews/glacial-v02-decb368`,
venv `D:/mandala/.venvs/glacial-review` (Python 3.11), Prüfskripte und Rohdaten in `D:/mandala/.reviews/work/`.

**Prüftiefe:**
- Jeder Befund ist entweder am Code nachgerechnet oder durch ein eigenes Skript reproduziert. Das Skript ist jeweils angegeben.
- „Gelesen“ heißt: nur von Hand geprüft, ohne Lauf.

## Kurzfazit

- **Der wissenschaftliche Kern ist korrekt implementiert.** Das gilt für ETAS-Likelihood, Kompensator, analytischen Gradienten, bedingte Kovarianz, Simulator, Tanaka-Phase und Gardner–Knopoff.
- **v0.1.0 bleibt unverändert.**
- **Blockierend für einen Merge ist nur ein Punkt (B1):** Die SE-Kalibrierung, auf der der eingefrorene Faktor 1,25 beruht, wurde nicht mit der Statistik der Produktion gerechnet. Nachgerechnet reicht 1,25 für den Trend, für das H2.2-Fensterverhältnis aber nicht. **An den veröffentlichten Klassifikationen ändert das nichts** (Details unten).
- **C2:** Mein Verdacht auf eine Größenverzerrung (Jensen) ist per Simulation widerlegt. Der Test hält α oder ist konservativ (K0). Wichtig ist nur W2.

## Befunde

### B1 – blockierend: SE-Kalibrierung ≠ Produktionsstatistik (bestätigt Codex P2 und erweitert ihn)

`scripts/v02_calibration_study.py:27-38` und `scripts/v02_recovery_study.py:19,48-63` weichen in vier Punkten von `v02.m2_region` (`v02.py:45-48,264-278`) ab:

1. **Fenster (Codex-Fund):** `window_ratio(f, (2008, 2019), (2020, 2025))`. Bei halboffenen Jahres-Bins und `t_end <= Ende` sind das die Bins 2008–2018 gegen 2020–2024, also 11 gegen 5. Die Produktion nutzt `WIN_A, WIN_B = (2008, 2020), (2020, 2026)`, also 12 gegen 6.
2. **Zeitraum:** Simuliert und gefittet wird 1995–2025 (30 Bins), die Produktion fittet 1995–2026 (31 Bins).
3. **Vorgeschichte:** Die Simulation beginnt bei t0. Die Produktion gibt 5 Jahre Ereignisse vor t0 als Auslöser mit (`HISTORY_YEARS`).
4. **p-Regime:** Wahres p ist 1,15. In 7 von 8 Regionen liegt das geschätzte p an der Untergrenze 1,0001.

Außerdem setzt sich die eingefrorene Basis „48 Kataloge, sd(z) = 1,11 / 1,18“ aus 40 Kalibrierkatalogen (rw_sd = 1) und den 8 stationären Two-Stage-Läufen der Recovery-Studie zusammen. Das habe ich exakt reproduziert: 1,106 / 1,176. Diese Mischung ist im Dokument nicht erklärt.

**Nachrechnung mit Produktionsgeometrie** (`work/calib_prod.py`):
- Simulation 1990–2026, Fit `[1995, 2026)` mit Jahreskanten, tmax 1, rw_sd 1, Produktionsfenster.
- 48 Seeds je Variante.
- Spalte „sd(z)“: Wert mit oberer 90-%-Bootstrap-Schranke in Klammern.

| wahres p | sd(z) Trend | sd(z) Fenster (Produktion) | sd(z) Fenster (Skriptfenster) |
|---|---|---|---|
| 1,02 | 1,02 (1,14) | **1,30 (1,42)** | 1,25 (1,37) |
| 1,15 | 1,11 (1,22) | **1,21 (1,35)** | 1,14 (1,25) |

**Folge:**
- Mit den Skriptfenstern reproduziert sich bei p = 1,15 die eingefrorene Basis (1,14, obere Schranke 1,25). Allein die korrekten Fenster heben sd(z) auf 1,21, im p-Regime an der Untergrenze auf 1,30.
- Für H2.1 (Trend) ist 1,25 konservativ.
- Für H2.2 (Fenster) ist 1,25 zu klein.
- Ich habe nachgerechnet, ab welchem Gesamtfaktor eine veröffentlichte H2.2-Klasse kippt: SE Alaska („background rise“) erst ab etwa 1,56, NZ Southern Alps („genuine quiet“) erst um 2,0. **Keine Klasse ändert sich bei ≤ 1,42.**

**Vorschlag:** Beide Skripte importieren `FIT_T0, FIT_T1, WIN_A, WIN_B, HISTORY_YEARS` aus `v02` statt Literalen. Die Kalibrierung mit Produktionsgeometrie wird neu gerechnet, auch im p-Regime an der Untergrenze. Ein Test sichert die Gleichheit der Konstanten ab. Da der Faktor in der Präregistrierung eingefroren ist, gehört die Korrektur in ein **dokumentiertes Erratum/Addendum**; der eingefrorene Wert wird nicht still geändert. Die Entscheidung liegt bei Johann.

### K0 – klein (geprüft, als Größenproblem widerlegt): C2-Referenz und neue Größe sind unterschiedlich definiert

`v02.stage_base` (`v02.py:434-438`) setzt `log_mu_ref` auf den **Mittelwert der jährlichen log µ** (2016–2025, Jahresfit mit Strafterm). `confirmatory_v02.region_change` (`confirmatory_v02.py:29-38`) vergleicht damit den **log eines über das Fenster konstanten µ** (`mu_window_mle`, ohne Strafterm). Nach Jensen wäre bei Jahr-zu-Jahr-Streuung ein positiver Versatz von etwa σ²/2 zu erwarten. Die eingefrorenen σ_year sind 0,358 (SE Alaska) und 0,155 (Interior).

**Simulation unter H0** (`work/c2_null.py`, 300 Wiederholungen je Szenario, eingefrorene Triggerparameter, Referenz exakt wie in `stage_base`):

| Szenario | Look | mittleres D (± SE) | sd(z) | Ablehnungsrate (nominal) |
|---|---|---|---|---|
| reines ETAS (σ_year 0,24 / 0,14) | 2029 | +0,016 ± 0,012 | 0,76 | 0,3 % (1 %) |
| reines ETAS | 2036 | −0,000 ± 0,008 | 0,90 | 2,3 % (4 %) |
| mit Jahresstreuung (σ_year 0,33 / 0,14) | 2029 | −0,022 ± 0,016 | 0,95 | 1,0 % (1 %) |
| mit Jahresstreuung | 2036 | −0,027 ± 0,011 | 1,05 | 3,0 % (4 %) |

**Ergebnis:**
- Der erwartete positive Versatz tritt nicht auf. Mit Jahresstreuung ist er sogar leicht negativ.
- Der Test hält sein Niveau oder ist konservativ. **Kein Handlungsbedarf für die Validität von C2.**
- Für die Lesbarkeit wäre es trotzdem sauberer, Referenz und neue Größe gleich zu definieren, z. B. als Referenz `mu_window_mle(…, 2016, 2026)`. Das ginge nur per Addendum vor dem 2027-01-01. Optional.
- Einschränkung: Im Modell ist die Streuung lognormal mit Median 1 und unabhängig von Jahr zu Jahr. Trends in der Referenzperiode und Netzwerkänderungen sind nicht abgebildet.

### W2 – wichtig: `evaluate_pair` bricht bei unbekanntem Look nicht ab

`confirmatory_v02.py:61`: `alpha = dict(LOOKS).get(look_end, np.nan)` vergleicht Floats exakt. Wer als Look-Ende das Dezimaljahr für 2029-12-31 übergibt (≈ 2029.997, so steht es in der JSON), bekommt `alpha = NaN` und `reject = False`. Es gibt keinen Fehler.

**Vorschlag:** Bei einem `look_end`, der nicht in `LOOKS` steht, `ValueError` werfen. Außerdem in der Präregistrierung festhalten, dass das Ende exklusiv ist (2030.0 bzw. 2037.0).

### W3 – wichtig: Stufe-1-Unsicherheit fehlt in der µ-Kovarianz (Prüfpunkt 1)

`fit_nonstationary(..., fix_trig=...)` liefert korrekt die *bedingte* Kovarianz des µ-Blocks; der Triggerblock ist null.
- Gegen eine eigene numerische Hesse-Matrix ist die Abweichung 4,7e-11. Die Straffunktion verkleinert die SE um etwa 1,4 %.
- Stufe 1 ist aber schlecht bestimmt. Im Testkatalog ist p = 1,33 ± 0,22 bei wahrem p = 1,15.
- In der Nachkalibrierung mit wahrem p = 1,02 liegt das geschätzte p in 27 % der Fälle an der Untergrenze und in 12 % an der Obergrenze 2,5.

Das deckt nur der empirische Faktor ab (B1). **Vorschlag:** Im Docstring und in METHODS sagen, dass die Kovarianz bedingt ist. Optional die SE per parametrischem Bootstrap über Stufe 1 bestimmen.

### K1 – klein: `tidal_phase` liefert 1–3 % NaN, nicht zufällig verteilt (Prüfpunkt 3)

Bei `half_window_h = 14` fehlt bei 1,0–3,0 % der Ereignisse ein Extremum auf einer Seite (`work/check_tides.py`, 3000 Zufallszeiten je Region). Diese Ereignisse liegen gehäuft nahe den Maxima und Minima. Mit ±20 h gibt es 0 % NaN.

Der Effekt auf Schuster ist bei 3 % klein (≪ MDE 6,8 %), aber es ist ein vermeidbarer Auswahleffekt. Das 5-Minuten-Raster ist ausreichend: Der Phasenfehler gegenüber 1 Minute ist im 99. Perzentil kleiner als 1,8°.

**Vorschlag:** `half_window_h = 20` setzen und die Anzahl der NaN pro Region in den Ergebnissen ausweisen.

### K2 – klein: Magnituden-Rundung im Simulator (Prüfpunkt 2)

`simulate` (`etas_nonstat.py:522,546`) zieht kontinuierliche Magnituden ab Mc und rundet erst danach. Dadurch umfasst das Label Mc nur [Mc, Mc+0,05).
- Anteil des untersten Bins: 0,106 statt 0,206 bei binned GR.
- Aki–Utsu b mit Bin-Korrektur: 0,895 statt 1,0 (n = 39 671).

Für die µ-Kalibrierung ist das harmlos. K, α und b-Wert-Tests auf simulierten Katalogen sind aber leicht verzerrt.

**Vorschlag:** Ab `mc - 0.05` ziehen und nach dem Runden auf ≥ Mc filtern.

### K3 – klein: Fehlende Tests (Prüfpunkt 7)

- Ein Test, der die Kalibrier- und Recovery-Konstanten an `v02` bindet. Er hätte B1 abgefangen.
- Gradiententest auch an der p-Untergrenze und mit Ereignissen vor t0. Beides habe ich geprüft (`work/check_etas.py`): Abweichung ≤ 6e-7.
- GK-Vorbeben, Vorrang der größeren Magnitude, gleiche Magnitude. Der vorhandene Test deckt nur Nachbeben ab.
- `tidal_phase` an Fensterrändern bzw. Anteil der NaN.
- `evaluate_pair` mit unbekanntem Look (W2).

Die Recovery-Tests nutzen feste Seeds. Sie sind deterministisch und nicht flaky. Weil sie auf 3 Seeds beruhen, sind sie aber nur Plausibilitätsprüfungen und keine Kalibrierung.

### K4 – klein: Plattformabhängigkeit, Windows (Prüfpunkt 8)

`tests/test_v02_prereg.py` schlägt unter Windows dreimal fehl (CI auf Ubuntu ist grün):
- **CRLF:** Ohne `.gitattributes` checkt autocrlf die Hash-geschützten Dateien mit CRLF aus. Der Index ist LF, die Arbeitskopie CRLF (`git ls-files --eol`). Die Daten selbst sind korrekt.
- **Encoding:** `read_text()` ohne `encoding` führt zu einem `UnicodeDecodeError` unter cp1252, weil `PREREGISTRATION_v0.2.md` Umlaute enthält. Dasselbe Muster findet sich in `v02.py:154,261,417,425`. Die eingefrorenen JSONs sind reines ASCII, praktisch also folgenlos.

**Vorschlag:** `.gitattributes` mit `results/frozen_*.json -text`, `PREREGISTRATION*.md -text` und `*.json -text`. Dazu überall `encoding="utf-8"`.

### K5 – klein: CI-Untergrenze von NumPy nicht getestet (Prüfpunkt 8)

`numpy>=1.26`, `pandas>=2.1` und `scipy>=1.11` werden in CI nie mit den Untergrenzen getestet, sondern nur mit den neuesten Versionen. **Vorschlag:** Einen Matrix-Job mit `pip install "numpy==1.26.*" "pandas==2.1.*" "scipy==1.11.*"` ergänzen oder die Untergrenzen anheben.

### K6 – klein: `simulate(p=1.0)`

Wenn Nachfolger entstehen, bricht die Funktion mit `ZeroDivisionError` ab (`etas_nonstat.py:536`). Über den Fit ist das nicht erreichbar, weil die Grenze bei p ≥ 1,0001 liegt. **Vorschlag:** Den Fall p = 1 analog zu `kint` behandeln (log-Inverse) oder `ValueError` werfen.

## Ohne Befund

| Prüfpunkt | Ergebnis | Tiefe |
|---|---|---|
| 1 Likelihood | Kern bis tmax gekappt, Ereignisse vor t0 nur als Auslöser (`target`), Bins und Exposition korrekt. Kompensator gegen Quadratur: 1,1e-11 (20 Ereignisse vor t0, 20 im Ziel) | gelesen + `check_etas.py` [b] |
| 1 Gradient | Alle vier Ableitungen von Hand hergeleitet. Gegen zentrale Differenzen: 1,5e-8 (p 1,2), 5,6e-7 (p 1,0001), 4,2e-7 (p 1,00005) | gelesen + [a] |
| 2 Simulator | Omori-Inverse-CDF gegen gekappte Kern-CDF: KS p = 0,80 (p 1,15 und 1,0001). Ausdünnung des Hintergrunds korrekt | [d] |
| 3 Phase | Konvention 0° Max, ±180° Min, steigend; Indizes der Extremum-Erkennung korrekt | gelesen + `check_tides.py` |
| 4 GK | Fenster nach van Stiphout et al.; absteigende Magnitude; Vor- und Nachbeben symmetrisch in T, räumlich L | gelesen |
| 5 v0.1.0 | `git diff v0.1.0 decb368 -- results/frozen*` zeigt nur die zwei neuen Dateien. `tipping.run_scenarios` mit `rheologies=None` ist identisch. Sonst nur Version, `__init__` und CLI-Unterbefehl geändert | git |
| 6 RAM | `pairs()` braucht in der Spitze 49 B/Paar (gemessen) und hält 16 B/Paar. Bei 15 M Paaren sind das etwa 0,74 GB, passend zum Benchmark | `check_etas.py` [f] |
| 6 Overflow | exp(α·ΔM) ≤ e^18, (Δt+c)^-p ≤ 1e15 innerhalb der Grenzen | gelesen |
| 8 Lint | ruff und `mypy --strict` lokal sauber; CI grün (Lint, 3.11, 3.12) | Lauf |

**Hinweis zum alten Prüfskript:** Das in der abgebrochenen Session vorbereitete `check_etas.py` hätte in Test [f] 400 000 Ereignisse in 20 Jahren erzeugt. Das sind rund 8·10⁹ Paare und weit über 100 GB RAM. Ich habe den Test vor dem Lauf auf 10 000 Ereignisse verkleinert.
