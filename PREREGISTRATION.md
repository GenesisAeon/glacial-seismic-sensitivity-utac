# Versuchsreihe & Präregistrierung „Frühstadium“ (P133, KLIMA-KRYO-13)

**Eingefroren am 2026-10-10** (Paketversion 0.1.0). Die eingefrorenen Zahlen stehen maschinenlesbar in
[`results/frozen_confirmatory_parameters.json`](results/frozen_confirmatory_parameters.json).
Abweichungen werden nur mit Datum und Begründung in [`CHANGELOG.md`](CHANGELOG.md) dokumentiert.
Die Datei selbst wird nicht umgeschrieben.

*English summary at the end.*

---

## 0. Was ist hier wirklich präregistriert?

| Teil | Status |
|---|---|
| Retrospektive Tests 1990–2025 (F1–F4, Indikator-Batterie) | **Nicht** präregistriert im strengen Sinn: Die Hypothesen wurden formuliert, *nachdem* in Phase 2 dieselben Daten explorativ angesehen worden waren. Dazu gehören die SE-Alaska-Saisonalität und die Amplitudenänderung zwischen den Hälften 1990–2007 und 2008–2025. Diese Tests sind deshalb als **vorab festgelegte, aber datenberührte Analysen** zu lesen. |
| Konfirmatorischer Test C1 auf Daten **ab 2026-11-01** | **Präregistriert.** Die Daten existieren zum Zeitpunkt des Einfrierens noch nicht. Alle Stellschrauben sind eingefroren: Mc, Declustering-Schwelle, Phase, Basiswert, Look-Termine und α. |

`honesty.are_retrospective_1990_2025_tests_preregistered()` gibt deshalb `False` zurück.

## 1. Fragestellung

Johann Römers Frühstadium-Argument hat zwei Teile:

1. Die Mantelantwort auf Eisentlastung ist verzögert. Beispiele sind die end-glazialen Pärvie-Brüche
   und der ~600-Jahre-Lag im isländischen Vulkanismus (Swindles et al. 2018). Ein flacher Trend der
   Bebenraten heute ist deshalb **keine Entwarnung**.
2. Der empfindlichere Test ist daher nicht der **Trend**, sondern die **Empfindlichkeit**. Löst
   *dieselbe* saisonale Entlastung im Lauf der Zeit *mehr* Beben aus?

## 2. Hypothesen und Tests

### F1 – Wachsende saisonale Modulation (harmonisches Modell, 1990–2025)

Poisson-GLM auf monatliche Zahlen declusterter Beben ≥ Mc mit **Jahres-Fixed-Effects**:

    log μ_t = α_Jahr(t) + (β0 + β1·τ_t) · cos(2π((m_t − 0,5)/12 − φ)),   τ_t = (t − 2008)/10

- φ ist die mittlere Phase 1990–2025 (Schuster). β0 ist die relative Saisonmodulation, β1 ihre Änderung pro Jahrzehnt.
- Die Jahres-Fixed-Effects absorbieren jede Ratenänderung von Jahr zu Jahr, auch Netzverdichtungen und Mc-Sprünge. Übrig bleiben nur Kontraste *innerhalb* eines Jahres.
- **H_F1:** β1 > 0, einseitig.
- **Primärregion:** `SE_Alaska_AK` (AEC-Katalog, M ≥ 2,1, ≤ 40 km).
- **Statistik:** quasi-Poisson-Wald-Test (SE nie kleiner als Poisson) und Permutationstest (2000 Permutationen). Dieser vertauscht die Zuordnung Jahr → τ und lässt die 12 Monate jedes Jahres intakt.
- **Sekundär:** alle übrigen Regionen mit ≥ 300 Ereignissen, Benjamini-Hochberg über alle Regionen.

### F2 – Wachsende Empfindlichkeit pro kPa (Lastmodell, GRACE 2002–2025)

    log μ_t = α_Jahr(t) + (γ0 + γ1·τ_t) · U_{t−3}

- **U** ist die saisonale Entlastung in kPa: −(GRACE-Massenanomalie − gleitendes 13-Monats-Mittel), regional gemittelt über die GSFC-Mascons der Box. Es gilt 1 cm w.e. = 0,0981 kPa.
- **γ0** ist die Ratenänderung pro kPa („Empfindlichkeit“), **γ1** ihre Änderung pro Jahrzehnt.
- **H_F2:** γ1 > 0.
- **Lag:** 3 Monate (vorab, nach Johnson et al. 2020). Die Lags 0–8 Monate werden nur explorativ gescannt.

### F3 – Regen vs. Eis/Schnee

- **Regressoren:** ERA5-Monatsanomalien (Open-Meteo-Archiv) von Niederschlag, Regen und Schneefall an festen Stützpunkten.
- **Modellvergleich:** Last allein, Regen allein, Schneefall allein, Last + Regen, alle drei; Bewertung per QAIC mit gleichem Dispersionsparameter.
- **Rein deskriptiv.** Eine Zuordnung gilt nur als „gelungen“, wenn die Regressoren nicht stark korreliert sind (|r| < 0,5) **und** ΔQAIC < −2 gilt.

### F4 – Gruppen

- **Gruppen:** Gebirgsgletscher (SE-Alaska, Alpen, Patagonien, Himalaya/Karakorum, Neuseeland, Island/Vatnajökull) vs. Eisschilde (Grönland, Westantarktis) vs. Kontrollen.
- **Gepoolt** werden β1, γ0 und γ1 per inverser Varianz, getrennt nach „Tier“: nationale Netze vs. ComCat M ≥ Mc. Die Tiers überlappen räumlich und werden nie gemeinsam gepoolt.
- **Explorativ.**

### F5 – Lag-/Detektionsmodell

Szenariorechnung, kein Test. Details in [`docs/LAG_MODEL.md`](docs/LAG_MODEL.md).

### Kritikalitäts-Batterie (aus Phase 2 übernommen)

- 2-Jahres-Bin-Indikatoren und CSD-Indikatoren mit Trendtests.
- Benjamini-Hochberg über alle Tests, Gruppen-Permutation getrennt nach Tier.

## 3. Konfirmatorischer Test C1 (präregistriert)

- **Daten:** dieselben Quellen und Filter wie oben, Ereignisse von **2026-11-01** bis zum Look-Termin.
- **Eingefroren pro Region:** Mc, log10 η0 (Declustering-Schwelle), Phase φ, Basiswert b_ref = β0 (1990–2025) und dessen SE.
- **Declustering:** Der gesamte Katalog ab 1990 wird mit der *eingefrorenen* Schwelle bearbeitet. Damit finden frühe Nachbeben im neuen Zeitraum ihre Eltern. Getestet werden nur Hintergrundereignisse im neuen Zeitraum.
- **Statistik:** harmonisches Poisson-Modell mit 12-Monats-Block-Fixed-Effects (Nov–Okt). Daraus ergibt sich b_new.
- **Teststatistik:** z = (b_new − b_ref) / √(se_new² + se_ref²), einseitig. **H_C1:** b_new > b_ref.
- **Looks:**
  - Look 1: Daten bis **2029-10-31**, α = 0,01.
  - Finaler Look: Daten bis **2036-10-31**, α = 0,04.
  - Gesamt-α 0,05 für die Primärregion (Bonferroni-Aufteilung).
- **Primärregion:** `SE_Alaska_AK`. Alle anderen Regionen sind sekundär (BH je Look).
- **Ausführung:** `python -m glacial_seismic_sensitivity_utac.confirmatory 2029-10-31`, nach `GSS_END=… glacial-sensitivity fetch --force`.

### Power (aus `results/confirmatory_power.csv`, analytisch; Monte-Carlo-Check im Test)

Für `SE_Alaska_AK` (≈ 178 declusterte Ereignisse/Jahr, φ ≈ 1,35, b_ref = 0,104 ± 0,024):

| Look | erwartete Ereignisse | MDE (b_new − b_ref, Power 80 %) | Power, falls der Punktschätzer β1 = 0,035/Jahrzehnt stimmt |
|---|---|---|---|
| 2029 | ~535 | 0,24 | ~8 % |
| 2036 | ~1784 | 0,12 | ~53 % |

Der finale Look kann also etwa eine **Verdopplung** der heutigen Modulation erkennen. Die Fortsetzung
des retrospektiven Punktschätzers würde er nur mit ~50 % Wahrscheinlichkeit finden. Ein Nicht-Befund
2036 wäre deshalb **keine** starke Evidenz gegen das Frühstadium. Das wird hier vorab festgehalten.

## 4. Interpretation (vorab festgelegt)

| Ergebnis | Lesart |
|---|---|
| β1, γ1 > 0 signifikant, Kontrollen nicht | Wachsende Empfindlichkeit, vereinbar mit dem Frühstadium. Rate-and-State erwartet für Perioden ≫ t_a aber α ≈ 2πΔS/(T·Ṡ), und zusätzliche GIA-Spannungsrate *senkt* die Modulation. Wachstum spricht daher eher für sinkende effektive Normalspannung (Porendruck, vgl. Mont Blanc, Simon et al. 2025) oder Annäherung an das Versagen (Parkfield-Befund bei Sirorattanakul & Avouac 2026). Kausalität ist damit **nicht** gezeigt. |
| β1 > 0 auch in Kontrollen | Netz-/Detektions-Artefakt (saisonales Mc) wahrscheinlicher |
| β1 ≈ 0, enges KI | Keine messbare Empfindlichkeitszunahme *in diesem Zeitraum und dieser Magnitude*. Das schließt eine verzögerte Antwort nicht aus (siehe Lag-Modell). |
| β1 < 0 | Abnehmende Modulation. Vereinbar mit steigender Hintergrund-Spannungsrate (RSM) **oder** mit geringerer saisonaler Last |

## 5. Änderungsregeln

- Wechselt ein Netz seine Magnitudenskala oder sein System (z. B. AEC-Katalogumstellungen), wird der Test trotzdem wie eingefroren ausgeführt. Zusätzlich gibt es eine dokumentierte Sensitivitätsvariante.
- Fehlende Monate (Datenausfall) werden nicht imputiert. Ein Block mit 0 Ereignissen fällt aus.
- Werden Daten rückwirkend revidiert, gilt der Katalogstand zum Look-Termin + 30 Tage. Die verwendete Datei wird archiviert.

## 6. Ergänzung vom 2026-10-10 (v0.1.0): Monitoring-Indikatoren M1–M5 und Hypothese B

Diese Ergänzung **ändert C1 nicht**. Sie legt zusätzliche Beobachtungsgrößen fest, die vor dem ersten
neuen Datenpunkt eingefroren werden (`results/frozen_monitoring_indicators.json`, Schwellen in
`extensions.THRESHOLDS`). Sie sind Monitoring, keine konfirmatorischen Tests. Überprüfung jährlich,
erstmals mit GRACE-FO-Daten und Katalogen bis 2027-12.

### Indikatoren

| Nr. | Größe | Schwelle (Flag) | Begründung |
|---|---|---|---|
| M1 | GRACE: normierte Beschleunigung des Massenverlusts ξ = −A/\|v\| je Box (quadratisch + Jahres-/Halbjahresgang, AR(1)-korrigierter Fehler, ganzer Datensatz ab 2002) | ξ > 0,02/Jahr **und** untere 95-%-Grenze > 0 | Exponentielle Pfade mit Edwards et al. 2021 (Grönland 95. Perzentil SSP5-8.5, Gletscher Median) entsprechen ξ ≈ 0,02/Jahr; DeConto et al. 2021 (×10 in 40 Jahren) ξ ≈ 0,058/Jahr. Herleitung in `tipping.py`. |
| M2 | GNSS (NGL, IGS20): Beschleunigung der Hebung je Station, Sprünge aus der NGL-Sprungliste modelliert | z > 3 **und** gleiches Vorzeichen wie M1 in der zugehörigen Box | Unabhängige Bestätigung von M1. Ohne passendes M1 wird nur berichtet, nicht gedeutet (elastische Antwort, lokale Effekte). |
| M3 | Saisonale Modulation b (wie C1), zusätzlich die **Abnahme** | einseitig, Faktor 2,487 (α 0,05 / Power 0,8) | Rate-and-State: Steigt die Hintergrund-Spannungsrate, sinkt die relative Modulation. Vorab festgehalten: In keinem Kippszenario erreicht die Abnahme mit heutigen Katalogen bis 2100 z > 1,3. M3 ist praktisch blind. |
| M4 | b-Wert (Aki-MLE) gegenüber 2008–2019 | Δb ≤ −0,2 bei \|ΔMc\| < 0,2 | b sinkt mit der differentiellen Spannung (Schorlemmer et al. 2005). Explorativ. |
| M5 | Ruhe: Habermann-z (entclusterte Jahreszahlen, letzte 6 Jahre gegen die 12 davor) **und** ETAS-Verhältnis beobachtet/erwartet < 1 im letzten Fenster (ETAS-Fit 1995–2014.5, Fortschreibung) | Habermann-z ≤ −2 | Wyss & Habermann 1988; Ogata 1992. Ein ETAS-z ≤ −2 ohne Habermann-Stütze wird nur als „ETAS-only“ berichtet. Grund: Im Basislauf schlug es in 2 von 3 Kontrollregionen an (Fortschreibung großer früherer Sequenzen, Überdispersion). Diese Präzisierung wurde nach dem Basislauf auf retrospektiven Daten festgelegt, vor jedem prospektiven Datenpunkt. |

### Hypothese B – trügerische Ruhe vor dem Kippen (nicht als Nachwirkung)

**Frage:** Kann eine scheinbare Beruhigung als *Vorläufer* auftreten, während sich Massenverlust und
Hebung in Richtung Kippregime beschleunigen?

**Modell** (`tipping.py`): Ein Katalog mischt Störungen, die durch die Entlastung gefördert werden, mit
Störungen im Spannungsschatten (Anteil f; Hampel et al. 2010, Harris 1998). Die Schattenstörungen
folgen der exakten Dieterich-Gleichung.

- Eine Netto-Ruhe gibt es nur bei f > 0,5.
- Sie bleibt, bis die GIA-Spannungsrate die tektonische übersteigt. Erst dann kehrt sie sich um.
- Vorab festgelegte Kenngrößen je Szenario:
  - Beginn der Ruhe (−2 % gegenüber 2025);
  - Minimum;
  - frühestes nachweisbares Jahr;
  - Umkehrjahr.

**Entscheidungsregel** (`quiescence.classify`, in dieser Reihenfolge):

1. Kein M5-Flag (Habermann-z ≤ −2 und ETAS-Verhältnis < 1) → „keine Ruhe“.
2. Katalogartefakt, wenn eines davon zutrifft (Habermann 1991) → „Artefakt-Verdacht“:
   - der Median des jährlichen Mc steigt um ≥ 0,2;
   - die Magnituden verschieben sich (KS p < 0,01 und \|Δ mittlere Magnitude\| ≥ 0,1).
3. M1 (ξ > 0) oder M2 (Hebungsbeschleunigung z > 3) zeigt Beschleunigung → **Kandidat für trügerische
   Ruhe vor dem Kippen**.
4. Sonst (Verlust verlangsamt sich, keine Hebungsbeschleunigung) → **vereinbar mit echter Entspannung**.

**Unterstützende Kriterien** für „trügerisch“. Sie werden berichtet, sind aber nicht Teil der Regel:

- räumlicher Dipol: Aktivierung in geförderten Teilgebieten bei gleichzeitiger Ruhe in den übrigen
  (Gitterzellen z > +2 neben z < −2);
- saisonale Modulation sinkt, obwohl die saisonale Lastamplitude gleich bleibt.

**Echte Entspannung** zeigt dagegen:

- eine verlangsamte Last (ξ < 0);
- keine beschleunigte Hebung;
- eine saisonale Modulation, die proportional zur Lastamplitude sinkt.

**Vulkanische Episoden** (z. B. Bárðarbunga 2014–15, Sigmundsson et al. 2015) machen Fenster
unbrauchbar. Deshalb beginnen die ETAS-Testfenster erst 2016.

**Was B nicht leisten kann:**

- Ein Kandidat ist kein Nachweis.
- Die Schattenanteile f sind unbekannt.
- Die Kopplung κ zwischen Oberflächenentlastung und Coulomb-Spannung ist nicht eingeschränkt.

---

## English summary

- **Not preregistered:** The retrospective 1990–2025 tests were specified after exploratory contact with the same data and are labelled accordingly.
- **Preregistered:** the confirmatory test C1 on data from 2026-11-01 onward. It is frozen in `results/frozen_confirmatory_parameters.json`.
  - Statistic: increase of the year-fixed-effect harmonic modulation b over the 1990–2025 baseline, one-sided.
  - Looks: 2029-10-31 (α 0.01) and 2036-10-31 (α 0.04).
  - Primary region: SE_Alaska_AK.
- **Power:** By 2036 the test detects roughly a doubling of today's modulation. It has only ~50 % power for a continuation of the retrospective point estimate, so a null result would not be strong evidence against the early-stage hypothesis.
- **Amendment 2026-10-10 (v0.1.0, additions only, C1 unchanged):** monitoring indicators M1–M5 are frozen in `results/frozen_monitoring_indicators.json`.
  - M1: GRACE normalised loss acceleration ξ > 0.02/yr with lower 95 % bound > 0.
  - M2: GNSS uplift acceleration z > 3, concordant with M1.
  - M3: seasonal-modulation drop.
  - M4: b-value drop ≥ 0.2.
  - M5: Habermann or ETAS quiescence z ≤ −2.
- **Hypothesis B:** a deceptive pre-tipping quiet is classified by a fixed rule:
  1. no quiet;
  2. catalogue artefact (Mc rise or magnitude shift);
  3. quiet with accelerating loss/uplift = candidate deceptive quiet;
  4. otherwise consistent with genuine relaxation.
