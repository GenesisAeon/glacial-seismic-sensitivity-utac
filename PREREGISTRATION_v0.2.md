# Präregistrierung – Ergänzung v0.2 (P133, KLIMA-KRYO-13)

**Status:** eingefroren am 2026-10-10, **bevor** irgendeine v0.2-Hypothesenanalyse (M2, M3) auf
echten Katalogdaten lief. Maschinenlesbare Fassung: `results/frozen_v02_preregistration.json`,
SHA-256 `af7a5d02b6d81e37ba989058968f913e5e821876f98926dcca924560d3d927d3`.
Belegt durch den Git-Commit auf dem Branch `v0.2-dev` (Zeitstempel auf GitHub). Die Archivierung
auf Zenodo erfolgt mit dem Release v0.2.0, das **vor dem 2027-01-01** erscheinen muss (Entscheidung
von J. Römer, siehe PR-Beschreibung).

Diese Ergänzung **ändert nichts an v0.1.0**: C1, die Monitoring-Indikatoren M1–M5 und alle
eingefrorenen Parameter bleiben unverändert. Die SHA-256 der beiden v0.1.0-Dateien sind in der
JSON-Datei festgehalten und werden von `tests/test_v02_prereg.py` geprüft:

| Datei | SHA-256 |
|---|---|
| `results/frozen_confirmatory_parameters.json` | `5bccd4cab0ba2d0143c4736c44355b24b6eb6356ca82ba0419fff22c71b4b3cb` |
| `results/frozen_monitoring_indicators.json` | `8ae57131325eda3ffb855f0437a649eb5adb0a32ae4e2fd0ec35f515cb87fb0f` |

**Ideengeber.** Mehrere Fragestellungen (zeitlich veränderlicher ETAS-Hintergrund, Gezeiten,
Viskositäten nach Sasgen et al. 2026) wurden durch einen Gemini-Deep-Research-Bericht angeregt.
Der Bericht ist **keine wissenschaftliche Quelle**; alle verwendeten Zahlen stammen aus den
unten zitierten Originalarbeiten. Die Faktenprüfung des Berichts liegt außerhalb des Repos.

## 1. Was ist neu präregistriert?

| Kürzel | Art | Daten | Entscheidung |
|---|---|---|---|
| H2.1 | retrospektiver Test | 1995–2025 | Trend des ETAS-Hintergrunds, Gletscher minus Kontrolle |
| H2.2 | retrospektive Klassifikation | 2008–2019 vs. 2020–2025 | „maskierter Hintergrundanstieg“ (Muster der trügerischen Ruhe) ja/nein |
| H3.1/H3.2 | retrospektive Tests | 1995–2025 | Gezeitenmodulation (Schuster), b-Wert nach Gezeitenphase |
| C2 | **prospektiver** Test | ab **2027-01-01** | Hintergrundänderung Gletscher vs. Kontrolle, eigenes Fenster |
| M6, M7 | Monitoring | ab 2027-01-01 | Flags, keine Tests |

H2 und H3 nutzen Daten, deren Gesamtraten in v0.1.0 bereits angesehen wurden (Habermann-z,
ETAS-Verhältnis). Sie sind deshalb **keine unabhängige Bestätigung**, sondern vorab festgelegte
Auswertungen einer neuen Größe (Hintergrundrate µ bzw. Gezeitenphase). Unabhängig ist nur C2.

## 2. Modell und Schätzer (H2, C2)

Zeitliches ETAS mit stückweise konstantem Hintergrund (Idee: Kumazawa & Ogata 2013,
doi:10.1002/2013JB010259):

    λ(t) = µ_y(t) + Σ_{t_j<t, t−t_j≤1 a} K·exp(α(m_j − Mc))·(t − t_j + c)^(−p)

* Ereignisse: alle Beben ≥ Referenz-Mc von v0.1.0 (nicht entclustert), gleiche Kataloge, Boxen und
  Tiefenfilter wie v0.1.0; Anpassungsfenster 1995-01-01 bis 2025-12-31, ein µ je Kalenderjahr;
  Beben der 5 Jahre davor wirken nur als Auslöser.
* `tmax` = 1 Jahr (wie v0.1.0; Benchmark M0: Speicherbedarf bei 1 Jahr ≤ 0,73 GB, bei 5 Jahren bis
  1,65 GB je Region).
* **Zweistufiger Schätzer** (`etas_nonstat.fit_two_stage`): (1) stationäres ETAS für (K, α, c, p);
  (2) jährliche log µ_y bei festgehaltenen Auslöserparametern, schwacher Random-Walk-Strafterm
  (σ = 1 in log µ). Begründung (synthetische Wiedergewinnungsstudie,
  `results/v02/recovery_study.csv`): Beim gemeinsamen Schätzer tauscht das Modell den langen
  Omori-Schwanz gegen die Jahres-µ (p um 0,3–0,6 zu hoch, Verzweigungsverhältnis ~0,33 statt ~0,5,
  µ um 25–30 % zu hoch) und die Standardfehler sind zu klein (sd(z) bis 2,0). Der zweistufige
  Schätzer ist besser kalibriert (sd(z) 0,8–1,4) und verzerrt den Trend höchstens leicht konservativ
  (−10 % bei linearem Anstieg).
* Standardfehler: SE = max(OLS-Residuen-SE, Likelihood-SE) × **1,25**. Der Faktor stammt aus
  48 stationären Nullsimulationen (sd(z) = 1,11 für den Trend, 1,18 für das Fensterverhältnis;
  obere 90-%-Bootstrapgrenze ≈ 1,25) und wird vorab festgelegt.

## 3. H2.1 – Trend des Hintergrunds

* Statistik je Region: OLS-Steigung von log µ_y (1995–2025) pro Jahrzehnt.
* Test: Differenz Gletscher − Kontrolle (gleiches Netz), einseitig > 0, z = Δ/√(SE_g² + SE_k²).
* Paare: **SE_Alaska_AK / Interior_AK_ctrl (primär, α = 0,05)**; NZ_Southern_Alps /
  NZ_Wellington_ctrl; Alps_SED / N_Switzerland_ctrl. Benjamini-Hochberg q = 0,05 über die drei Paare.
* Island (IMO) und Grönland (GEUS) nur beschreibend (keine netzinterne Kontrolle).
* Grenzen: Netzwerkänderungen, die Mc innerhalb der Referenz-Mc verschieben, wirken in beiden
  Regionen eines Netzes gleich nur, wenn sie gleichzeitig stattfinden; das ist nicht garantiert.

## 4. H2.2 – Klassifikation „trügerische Ruhe“

Verhältnis µ(2020–2025)/µ(2008–2019) aus den Jahreswerten (Welch-SE × 1,25, 95-%-Intervall) und
Verhältnis der Gesamtraten (alle Beben ≥ Mc) in denselben Fenstern:

| Klasse | Regel |
|---|---|
| maskierter Hintergrundanstieg (Muster der trügerischen Ruhe) | untere µ-Grenze > 1 **und** Gesamtverhältnis < 1 |
| Hintergrundanstieg (nicht maskiert) | untere µ-Grenze > 1 und Gesamtverhältnis ≥ 1 |
| Hintergrundabnahme (echte Ruhe) | obere µ-Grenze < 1 |
| keine auflösbare Änderung | sonst |

Beschreibend, ohne p-Wert. Ein „maskierter Anstieg“ in einer Gletscherregion zählt nur, wenn die
netzinterne Kontrolle nicht dieselbe Klasse zeigt. Ein solcher Befund wäre **kein** Beleg für ein
bevorstehendes Kippen; er zeigt nur, dass ein Rückgang der Gesamtrate durch abklingende Nachbeben
statt durch sinkenden Antrieb erklärt wird.

## 5. C2 – prospektiver Test ab 2027-01-01

* Statistik: D = [log µ_neu − log µ_ref]_Gletscher − [log µ_neu − log µ_ref]_Kontrolle, einseitig D > 0.
* µ_neu: konstantes µ, ML-Schätzung auf [2027-01-01, Ende des Blicks) mit **eingefrorenen**
  Auslöserparametern (`etas_nonstat.mu_window_mle`); Beben des Vorjahres nur als Auslöser.
* µ_ref: Mittel von log µ_y 2016–2025 aus dem H2-Lauf; σ_y: deren Jahresstreuung.
* SE² = Σ_Regionen (se_neu² + σ_y²/T + σ_y²/n_ref), T = Fensterlänge in Jahren, n_ref = 10.
* Blicke: Daten bis **2029-12-31 (α = 0,01)** und bis **2036-12-31 (α = 0,04)**.
* Primäres Paar: SE_Alaska_AK / Interior_AK_ctrl (einziger Test, keine Multiplizität).
  Die anderen beiden Paare werden nur beschreibend berichtet.
* Baselines (Mc, K, α, c, p, log µ_ref, σ_y) werden aus Daten bis 2025-12-31 berechnet, in
  `results/frozen_v02_baselines.json` eingefroren und gehasht – vor 2027-01-01.
* C2 ist von C1 unabhängig; C1 bleibt unverändert.

## 6. H3 – Gezeiten (Körpergezeit)

* Grad-2-Gezeitenpotential von Mond und Sonne (eigene Ephemeride nach Meeus, geprüft an den
  Beispielen 47.a und 25.a), Flächendehnung (2h − 6l)·W2/(g·a), h = 0,6114, l = 0,0832.
  **Ohne Ozeanauflast** – in Küstenregionen kann sie die Körpergezeit übertreffen; ein Nullbefund
  schließt Gezeitenauslösung daher nicht aus.
* Phase nach Tanaka et al. 2002 (JGR 107:2211): 0° im Dehnungsmaximum, ±180° in den Minima.
* Ereignisse: v0.1.0-entclusterte Beben ≥ Mc, 1995–2025.
* H3.1: Schuster-Test, p = exp(−R²/N). H3.2: b(|Phase| < 90°) < b(|Phase| ≥ 90°), einseitig
  (z mit Shi-Bolt-SE; Likelihood-Quotient zusätzlich berichtet), Richtung nach Tan et al. 2019.
* Testregionen: SE_Alaska_AK, NZ_Southern_Alps, Alps_SED, Iceland_Vatnajokull_IMO, Greenland_GEUS;
  BH q = 0,05 je Hypothese über diese fünf. Kontrollen beschreibend.
* Power: kleinste nachweisbare Modulationsamplitude a (Rate ∝ 1 + a·cos Phase) und Δb bei
  α = 0,05, Power 0,8, per Simulation.

## 7. Monitoring (ab 2027-01-01, keine Tests)

| Nr. | Größe | Flag |
|---|---|---|
| M6 | Hintergrundanstieg einer Gletscherregion allein: z = (log µ_neu − log µ_ref)/SE | z ≥ 2 |
| M7 | Schuster-Test im neuen Fenster (entclustert mit eingefrorener NN-Schwelle), N ≥ 200 | p < 0,01 |

Überprüfung jährlich, erstmals mit Katalogen bis 2027-12-31.

## 8. Änderungsregeln

Jede spätere Änderung ist ein neuer, datierter Nachtrag mit neuem Hash; die ursprüngliche Datei
bleibt in der Git-Historie. Nach dem 2027-01-01 werden C2-Regeln nicht mehr geändert.

## Quellen

* Kumazawa, T. & Ogata, Y. (2013): Quantitative description of induced seismic activity before and
  after the 2011 Tohoku-Oki earthquake by nonstationary ETAS models. JGR 118:6165.
  https://doi.org/10.1002/2013JB010259
* Tanaka, S., Ohtake, M. & Sato, H. (2002): Evidence for tidal triggering of earthquakes as revealed
  from statistical analysis of global data. JGR 107(B10):2211. https://doi.org/10.1029/2001JB001577
* Tan, Y. J., Waldhauser, F., Tolstoy, M. & Wilcock, W. S. D. (2019): Axial Seamount: Periodic tidal
  loading reveals stress dependence of the earthquake size distribution (b value). EPSL 512:39–45.
  https://doi.org/10.1016/j.epsl.2019.01.047
* Sasgen, I. et al. (2026): Commun. Earth Environ. 7:518. https://doi.org/10.1038/s43247-026-03738-y
* Meeus, J. (1998): Astronomical Algorithms, 2nd ed., Willmann-Bell (Kap. 25, 47).

## English summary

Addendum frozen on 2026-10-10 before any v0.2 hypothesis analysis on real data; JSON SHA-256
`af7a5d02b6d81e37ba989058968f913e5e821876f98926dcca924560d3d927d3`. v0.1.0 (C1, M1–M5, all
frozen parameters) is unchanged; the hashes of its frozen files are recorded and tested.
**H2.1**: OLS trend of the yearly ETAS background log µ (two-stage estimator, tmax 1 yr, SE × 1.25
from null simulations), glacier minus network-internal control, one-sided; primary pair SE Alaska /
Interior Alaska (α 0.05), BH over three pairs. **H2.2**: descriptive classes, incl. "masked
background rise" (µ ratio 2020–25 vs 2008–19 lower 95 % bound > 1 while the total rate falls).
**H3**: body-tide (no ocean loading) Schuster test and tidal b-value split in five glacier
regions, BH. **C2** (independent, prospective): change of log µ from 2027-01-01 with frozen
triggering parameters, glacier minus control, looks at 2029-12-31 (α 0.01) and 2036-12-31
(α 0.04). Baselines are frozen and hashed before 2027. Monitoring flags M6 (background rise) and
M7 (tidal Schuster p < 0.01). The Gemini report is credited as an idea source only.
