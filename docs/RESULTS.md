# Ergebnisse (Lauf vom 2026-10-10, Daten bis 2025-12-31)

Alle Zahlen stammen aus den CSV-Dateien in [`../results/`](../results/) und lassen sich mit
`glacial-sensitivity run` reproduzieren. Charts liegen in [`../charts/`](../charts/).
Hier wird nur berichtet; die Lesart ist in [`../PREREGISTRATION.md`](../PREREGISTRATION.md) §4 vorab
festgelegt, die Grenzen stehen in [`LIMITATIONS.md`](LIMITATIONS.md).

**Kurzfassung:** Kein Test zur *wachsenden* Empfindlichkeit ist nach Mehrfachtest-Korrektur signifikant.
Die Kritikalitäts-Indikatoren zeigen einzelne Treffer, die sich als Netz- und Rateneffekte erklären lassen
und in Kontrollregionen genauso auftreten.
Die saisonale Modulation in SE-Alaska ist robust vorhanden, wächst aber nicht messbar. Das Lag-Modell
zeigt, dass eine verzögerte viskose Antwort über Ratentrends praktisch nicht nachweisbar wäre – ein
flacher Trend ist also weder Entwarnung noch Beleg.

## F1 – Wachsende saisonale Modulation 1990–2025

`results/F1_harmonic_growth.csv`, Charts 03, 04a.

| Region (Tier) | Mc | Ereignisse | β0 (Modulation 2008) | β1 pro Jahrzehnt | p einseitig (Wald / Perm.) | q (BH) |
|---|---|---|---|---|---|---|
| **SE_Alaska_AK** (national, primär) | 2,1 | 5164 | 0,104 ± 0,024 | **+0,035 ± 0,023** | 0,064 / 0,100 | 0,38 |
| Alps_SED | 2,1 | 1314 | 0,033 ± 0,041 | +0,058 ± 0,039 | 0,067 / 0,079 | 0,38 |
| NZ_Southern_Alps | 2,8 | 4325 | 0,054 ± 0,023 | +0,038 ± 0,023 | 0,047 / 0,058 | 0,38 |
| Iceland_Vatnajokull_IMO | 2,5 | 1327 | 0,300 ± 0,062 | −0,096 ± 0,063 | 0,94 / 0,86 | 0,86 |
| Greenland_GEUS (Eisschild) | 2,7 | 514 | 0,022 ± 0,088 | +0,146 ± 0,088 | 0,048 / **0,0055** | 0,083 |
| SE_Alaska (ComCat) | 3,4 | 465 | 0,183 ± 0,066 | −0,031 ± 0,060 | 0,69 / 0,71 | 0,82 |
| Himalaya_Karakoram (ComCat) | 4,7 | 569 | 0,140 ± 0,065 | −0,045 ± 0,064 | 0,76 / 0,78 | 0,84 |
| Kontrollen (8 Regionen) | – | – | −0,008 … 0,094 | −0,008 … +0,092 | alle ≥ 0,10 / ≥ 0,13 | ≥ 0,40 |

- **SE-Alaska:** 95-%-KI für β1 ≈ [−0,010; +0,080] pro Jahrzehnt. Der Punktschätzer entspräche einer
  Modulation von ~0,04 (1990) auf ~0,16 (2025), ist aber mit null vereinbar. Die 6-Jahres-Fenster
  (`seasonal_amplitude_windows.csv`) verlaufen nicht monoton: 0,08 / 0,09 / 0,26 / 0,15 / 0,09 / 0,15.
- **Island** zeigt *abnehmende* Modulation (Fenster 0,54–0,57 in 1996–2007 → 0,10 in 2020–2025).
- **Grönland** ist der einzige Permutations-p < 0,01, liegt nach BH aber über 0,05. Verdacht auf
  Netz-/Detektionsartefakt: vor 2008 nur 11–22 Ereignisse pro 6 Jahre, November-Mc 2,4.
- **Gruppen-Meta** (`F_group_meta.csv`, explorativ):
  - Gebirge national: β1 = 0,033 ± 0,015 (z = 2,25; Q = 4,6 bei 4 Regionen).
  - Kontrollen national: −0,004 ± 0,012.
  - ComCat-Gebirge: −0,037 ± 0,044.
  - Der nationale Gebirgswert ist der auffälligste Einzelbefund, aber nicht präregistriert und nicht
    korrigiert. Er wird von Alpen, NZ und SE-Alaska getragen, Island zieht in die Gegenrichtung.

## F2 – Empfindlichkeit pro kPa (GRACE, 2002–2025, Lag 3 Monate)

`results/F2_load_sensitivity_growth.csv`, Charts 04b, 04c, 05, 06.

| Region | U-Streuung (kPa) | γ0 (%/kPa) | p (γ0 > 0) | γ1 (%/kPa pro Jahrzehnt) | p (γ1 > 0, Perm.) |
|---|---|---|---|---|---|
| **SE_Alaska_AK** | 2,45 | **4,0 ± 1,1** | 1·10⁻⁴ | −1,3 ± 1,1 | 0,94 |
| Iceland_Vatnajokull_IMO | 1,13 | 17,5 ± 6,3 | 0,003 | −10,6 ± 7,1 | 0,84 |
| NZ_Southern_Alps | 0,48 | 8,1 ± 5,3 | 0,064 | +7,1 ± 6,2 | 0,18 |
| Alps_SED | 0,60 | −5,5 ± 8,5 | 0,74 | −2,5 ± 9,5 | 0,62 |
| Interior_AK_ctrl | 0,60 | 4,3 ± 4,1 | 0,15 | +1,1 ± 4,3 | 0,45 |
| Japan (Kontrolle) | 0,36 | −14,2 ± 10,7 | 0,91 | +26,2 ± 11,4 | 0,021 (q 0,29) |

- **γ0 in SE-Alaska** (4,0 %/kPa) liegt nahe am Wert von Johnson et al. 2020 (3,5 %/kPa,
  doi:10.1016/j.epsl.2019.115904). Die Größen sind aber verschieden normiert (regional gemittelte
  GRACE-Last vs. modellierte Spannung auf Verwerfungen); die Nähe ist teils Zufall.
- **Keine wachsende Empfindlichkeit:** γ1 ist in SE-Alaska negativ; obere 95-%-Grenze ≈ +0,9 %/kPa pro Jahrzehnt.
- **Explorativer Lag-Scan** (Chart 06): SE-Alaska maximal bei 1–2 Monaten (~5,6–5,9 %/kPa).
- **Interior-Alaska-Kontrolle:** Punktschätzer γ0 (4,3 %/kPa) ähnlich wie SE-Alaska, aber
  viermal unsicherer, weil die saisonale Last dort klein ist. Das ist bei der Deutung von γ0 als
  „Gletschersignal“ zu beachten.
- **Gruppen-Meta:** Gebirge national γ0 = 4,4 ± 1,0 %/kPa (z = 4,2; heterogen, Q = 6,3); γ1 = −1,3 ± 1,1.

## F3 – Regen vs. Last

`results/F3_rain_vs_load.csv`, Chart 07.

- **SE-Alaska:** GRACE-Entlastung und ERA5-Regen korrelieren mit r = 0,68. Bei Lag 3 ist
  ΔQAIC −13,8 (Last), −11,5 (Regen), −13,5 (beide; z_U = 1,97, z_Regen = 1,27). **Nicht trennbar.**
  Bei Lag 0 sind Last und Schneefall praktisch gleichwertig (−12,6 / −12,6).
- **Neuseeland, Südalpen:** Last und Regen sind dort kaum korreliert (r = −0,06). Bei Lag 3 verbessert
  nur die Last das Modell (ΔQAIC −4,6; Regen +1,7). Das erfüllt das vorab festgelegte Kriterium für
  eine Zuordnung – **explorativ**, γ0 selbst ist mit p = 0,064 nicht signifikant.
- Alpen, Kontrollen: keine Verbesserung über |ΔQAIC| > 2 hinaus, die der Last zuzuordnen wäre.

## Saisonalität und Robustheit (Grundlage für F1/F2)

`results/seasonal_*.csv`, Charts 01, 02, 13.

- **SE-Alaska (AEC):** Schuster-Amplitude 0,11, p < 10⁻⁶, Maximum Mitte November. Robust über Tiefe,
  Magnitudenklassen und beide Hälften des Zeitraums. Die GRACE-Last ist im April maximal, die
  Entlastung U also etwa im Oktober; das Bebenmaximum liegt 1–2 Monate danach (passend zum Lag-Scan).
- **SE-Alaska (ComCat, M ≥ 3,4):** Maximum eher September (Amplitude 0,18, p = 0,024) – die Phase
  hängt vom Magnitudenbereich bzw. Katalog ab; mit nur 465 Ereignissen ist das unsicher.
- **Interior Alaska:** Amplitude 0,023 (p = 0,39). Kantishna allein 0,029 (p = 0,54), ohne
  Kantishna 0,026. Ein durch gegenläufige Phasen ausgelöschtes Signal gibt es auf regionaler Ebene
  nicht; die 1°-Karte (Chart 13) zeigt einzelne Zellen mit p < 0,05 unkorrigiert, aber kein Muster.
- **Himalaya (ComCat):** Maximum im Januar (Amplitude 0,15, p = 0,04), im Einklang mit dem
  Wintermaximum bei Bettinelli et al. 2008 (doi:10.1016/j.epsl.2007.11.021).
- **Alpen (SED):** praktisch keine Saisonalität (Amplitude 0,005).

## GRACE-Lasten

`results/grace_load_summary.csv`. SE-Alaska −1,71 kPa/Jahr (−36,7 Gt/Jahr, 17 Mascons), saisonale
Amplitude 3,1 kPa, Lastmaximum im April. Grönland −289 Gt/Jahr, Patagonien −25,8, Himalaya/Karakorum
−28,0, Island (Box) −8,4 Gt/Jahr. Die Alpen-Box (6 Mascons) ist mit −0,6 Gt/Jahr klein und verschmiert.

## F5 – Lag-Modell (Szenarien, kein Test)

Details in [`LAG_MODEL.md`](LAG_MODEL.md), Charts 08–10.

- Relaxationszeiten τ: Patagonien 23–117 Jahre, Amundsen ~55, SE-Alaska 64–170, SE-Grönland ~115,
  Island 150–380, Alpen 1000–2000, Fennoskandia ~4500.
- Schmale Gebirgslasten werden überwiegend elastisch, also sofort, beantwortet (Anteil des
  verzögerten Teils C: SE-Alaska 0,11, Alpen 0,18; SE-Grönland 0,94).
- Viskos verzögerter Ratenzuwachs selbst im oberen Szenario (κ = 1): ≤ +19 % bis 2036, ≤ +27 % bis
  2100; mit GRACE-Boxlast ≤ +5 %. Ein Trend wäre nur in 8 von 126 Szenarien nachweisbar, frühestens ~2155.
- Rate-and-State: Zusätzliche Spannungsrate *senkt* die saisonale Modulation. Wachsende Empfindlichkeit
  ist daher nicht die generische Erwartung.

## Konfirmatorischer Test C1 – Power

`results/confirmatory_power.csv`, Chart 11. Für SE_Alaska_AK: MDE (80 % Power) 0,24 beim Look 2029,
0,12 beim finalen Look 2036. Bei Fortsetzung des Punktschätzers β1 wäre die Power ~8 % bzw. ~53 %.

## Kritikalitäts-Batterie (aus Phase 2)

`results/criticality_*.csv`, Chart 12. Neu gerechnet mit 10 000 Block-Permutationen und 2000
IAAFT-Surrogaten. Der erste Lauf (2000 / 500) konnte wegen der p-Wert-Auflösung kein q < 0,058
erreichen und zeigte deshalb 0 Treffer; das war eine Grenze der Rechnung, kein Befund.

| Familie | Tests | p < 0,05 unkorrigiert | signifikant nach BH (q < 0,05) |
|---|---|---|---|
| Trendtests der 2-Jahres-Indikatoren (Kendall, Block-Permutation) | 374 | 63 | 10 |
| CSD-Indikatoren gegen IAAFT-Surrogate | 170 | 18 | 6 |
| Gruppenvergleiche Gebirge/Eisschild vs. Kontrolle (je Tier) | 180 | 2 | **0** (kleinstes q 0,76) |

**Die 16 BH-Treffer:**

- **Netz/Vollständigkeit (5):** Mc-Trends in Alps_SED, Alps (ComCat), Island (IMO) und
  N_Switzerland_ctrl; Anteil mb-Magnituden in SE_Alaska_AK (Magnitudentyp-Wechsel).
- **b-Wert (3):** Gleitfenster-b in NZ_Wellington_ctrl (roh und declustert) und Island (roh);
  b-Wert-Trend in Central_Andes (Kontrolle). b-Werte reagieren empfindlich auf Mc- und Skalenwechsel.
- **Cluster (1):** Zahl der Cluster ≥ 5 Ereignisse in Grönland (steigt mit dem Netzausbau).
- **CSD (6):** Varianz steigt in SE_Alaska_AK (nur roh, nicht declustert) und Grönland (roh und
  declustert), fällt in Alps_SED (declustert); Kurtosis Grönland, Schiefe Alps (ComCat).

**Lesart:**
- 4 der 10 Trend-Treffer liegen in Kontrollregionen, und kein Gruppenvergleich ist signifikant. Ein
  gletscherspezifisches Muster gibt es also nicht.
- Die klassischen Frühwarnzeichen einer kritischen Verlangsamung – steigende Autokorrelation (AR1) und
  sinkende Erholungsrate – sind **nirgends** signifikant. Steigende Varianz allein entsteht auch, wenn
  die Rate oder die Clusterhäufigkeit zunimmt (bei Zählungen wächst die Varianz mit dem Mittelwert);
  in Grönland fällt sie mit dem Netzausbau nach ~2008 zusammen.
- Die Treffer sind deshalb als Netz-, Katalog- und Rateneffekte zu lesen, **nicht** als Hinweis auf
  Kritikalität. Ausgeschlossen ist Kritikalität damit nicht; diese Indikatoren haben bei 18
  Zwei-Jahres-Bins wenig Power.

---

# Erweiterungen v0.1.0 (Lauf 2026-10-10, `glacial-sensitivity extensions`)

Alle Zahlen stammen aus den Dateien in `results/`, die unten jeweils genannt sind. Die Szenarien sind
**Modellrechnungen, keine Prognosen**. Die Kopplung κ zwischen Oberflächenentlastung und
Coulomb-Spannung auf den Störungen ist unbekannt. κ = 1 ist ein oberes Ende.

## Heute messbare Vorläufer (M1, M2) – `precursors_*.csv`, Chart 16

**GRACE/GRACE-FO 2002.3–2026.2.** v ist die Massenrate 2015, A die Beschleunigung, ξ = −A/|v|
(> 0 heißt: der Verlust beschleunigt sich). Die Fehler sind 1σ, AR(1)-korrigiert.

| Box | v [Gt/a] | A [Gt/a²] | ξ [1/a] | Rate 2002–13 → 2014–26 [Gt/a] | M1 |
|---|---|---|---|---|---|
| Amundsen-See (ASE) | −110,2 ± 2,5 | −0,94 ± 0,84 | +0,0085 ± 0,0076 | −100 → −108 | – |
| Grönland gesamt | −285,8 ± 6,3 | +5,3 ± 2,1 | **−0,019 ± 0,007** (Verlust verlangsamt sich) | −324 → −248 | – |
| Grönland SO | −96,0 ± 2,8 | +2,3 ± 0,9 | −0,024 ± 0,010 | −115 → −83 | – |
| Grönland W | −62,5 ± 2,6 | +1,7 ± 0,9 | −0,027 ± 0,014 | −70 → −47 | – |
| SE-Alaska | −37,1 ± 1,7 | −0,56 ± 0,57 | +0,015 ± 0,015 | −28 → −38 | – |
| Vatnajökull (1 Mascon) | −1,07 ± 0,02 | +0,023 ± 0,007 | **−0,022 ± 0,007** | −1,39 → −1,03 | – |
| Patagonien | −26,4 ± 0,6 | −1,04 ± 0,19 | **+0,039 ± 0,007** (e-Faltung ≈ 25 a) | −19 → −34 | **ja** |

- Nur **Patagonien** überschreitet die M1-Schwelle. Dort gibt es keinen brauchbaren Katalog: ComCat
  ist zu dünn, und der CSN-Katalog reicht nur bis 45,98° S.
- Grönland und Vatnajökull verlieren seit ~2014 *langsamer* (vgl. Bevis et al. 2019 zur Abhängigkeit
  von der atmosphärischen Zirkulation).
- In der Amundsen-See ist keine signifikante Beschleunigung messbar. Velicogna et al. 2020 beschreiben
  eine Pause der antarktischen Beschleunigung nach 2016.

**GNSS (NGL, IGS20, Sprünge modelliert).** Hebung 2015 und Beschleunigung (z).

- **M2-Flag (z > 3):**
  - TOMO (ASE): 41,7 mm/a; +2,31 mm/a² (z 8,0).
  - BACK (ASE): 13,1 mm/a; +0,67 (z 4,9).
  - AB50 (SE-Alaska): 19,0 mm/a; +0,46 (z 6,4).
  - KELY (W-Grönland): 7,2 mm/a; +0,48 (z 8,3).
- **Ohne Flag:**
  - HOFN (Vatnajökull): 12,3 mm/a; −0,005 (z −0,1). Die Hebung ist konstant.
  - INMN: z 2,6. KULU: z 2,0. JNU1: z 1,1.
  - QAQ1, THU2, LPLY: ≈ 0.
  - Kontrolle FAIR: −0,02.
- **Konkordanz mit M1:**
  - TOMO/BACK und AB50 haben dasselbe Vorzeichen wie ξ ihrer Box. ξ ist dort aber nicht signifikant.
  - KELY ist **diskordant**: Die W-Grönland-Box verlangsamt sich. Nach der Vorab-Regel wird KELY
    nur berichtet, nicht gedeutet.
  - Mögliche Ursachen: elastische Antwort auf die Verlusthistorie 2003–2012, lokale Effekte.
- TOMO bestätigt die von Barletta et al. 2018 gemessene Hebung (bis 41 mm/a).

## A – Kippszenarien → Seismizitätsverhältnis – `tipping_scenarios.csv`, `tipping_trajectories.csv`, Chart 14

**Pfade.** Der Lastfaktor m ist relativ zur heutigen GRACE-Rate.

- **Grönland:**
  - SSP5-8.5-Median-äquivalent: m(2100) = 2,1.
  - 95. Perzentil: 6,6. Das Integral 2015–2100 entspricht 10 bzw. 20 cm SLE (Edwards et al. 2021).
- **Amundsen:** DeConto ~3 °C, ×10 ab 2060; Sensitivitätsfall ab 2040.
- **Gebirgsgletscher:** global-glacier-SSP5-8.5-äquivalent, m = 5,2 ab 2015.
  - Illustrativ, denn Gletscher gehen aus.
- **Für jede Region zusätzlich:**
  - „Fortsetzung“ (m = 1);
  - „GRACE-Beschleunigung fortgesetzt“, exp(ξ·t).
- **Variierte Parameter:** κ ∈ {0,3; 1}, Ṡ0 ∈ {10; 30} kPa/a.

**Rate geförderter Störungen, relativ zu 2025** (Spanne über κ und Ṡ0) und frühester Nachweis des
Anstiegs (Trend ab 2026-11, heutige Katalograte):

| Region / Pfad | 2050 | 2100 | Nachweis Anstieg frühestens |
|---|---|---|---|
| Grönland SO, Edwards Median | 1,00–1,03 | 1,01–1,10 | 2158 (1 von 4) |
| Grönland SO, Edwards 95. Perz. | 1,00–1,04 | 1,02–1,24 | 2102 (3 von 4) |
| Grönland SO, GRACE-Trend fortgesetzt (verlangsamend) | ≈ 1,00 | ≈ 1,00 | nie |
| Amundsen, DeConto 3 °C (ab 2060) | 1,00–1,02 | 1,10–1,89 | 2079 (4 von 4)* |
| Amundsen, DeConto früh (ab 2040) | 1,01–1,06 | 1,11–1,96 | 2065 (4 von 4)* |
| SE-Alaska, Gletscher SSP5-8.5 (Last Gletscheroberfläche) | 1,04–1,26 | 1,21–2,35 | **2046** (4 von 4) |
| SE-Alaska, Gletscher SSP5-8.5 (Last GRACE-Box) | 1,01–1,09 | 1,05–1,46 | 2061 (4 von 4) |
| SE-Alaska, GRACE-ξ fortgesetzt (Oberfläche) | 1,03–1,19 | 1,14–1,86 | 2050 (4 von 4) |
| Island, Gletscher SSP5-8.5 (Oberfläche) | 1,03–1,19 | 1,13–1,99 | 2070 (4 von 4) |
| Island, GRACE-ξ fortgesetzt (verlangsamend) | 0,92–0,99 | 0,84–0,98 | nie |

\* Hypothetisches Netz mit 100 Ereignissen/a. Die Westantarktis hat heute keinen brauchbaren Katalog.

**Saisonale Modulation:** Sie sinkt in allen Beschleunigungspfaden, bis 2100 auf 0,43–0,97 des heutigen
Werts. Mit heutigen Katalogen erreicht die Abnahme bis 2100 aber höchstens z = 1,2 und ist damit
**nicht nachweisbar**.

**Lesart A:**

- Nur die steilsten Pfade machen einen Anstieg vor ~2060 nachweisbar:
  - Gebirgsgletscher mit hoher Kopplung;
  - Amundsen bei frühem Kippen und einem dichten, heute nicht existierenden Netz.
- Grönland bleibt bis 2100 im Rauschen.
- Die früheren 126 Szenarien mit konstanter Rate (Nachweis ≥ 2155) werden dadurch nicht widerlegt, sondern ergänzt: Erst eine Beschleunigung verkürzt die Nachweiszeit auf Jahrzehnte.

## B – Trügerische Ruhe vor dem Kippen – `tipping_scenarios.csv` (shadow_frac = 0,6), Chart 15

**Modell:** 60 % der Störungen liegen im Spannungsschatten. Das ist eine Annahme; eine Netto-Ruhe gibt
es nur bei f > 0,5.

| Pfad | Beginn (−2 %) | Tiefe (Minimum) | frühester Nachweis der Ruhe | Ende der Ruhe (Rate wieder ≥ 2025) |
|---|---|---|---|---|
| Amundsen, DeConto ab 2060 | 2070–2100 (10–40 a nach Beginn) | 0,87–0,96 | 2097 | 2126 (nur κ = 1, Ṡ0 = 10) |
| Amundsen, DeConto ab 2040 | 2055–2099 (15–59 a) | 0,86–0,96 | 2089 | 2120 |
| SE-Alaska, Gletscher SSP5-8.5 (Oberfläche) | 2032–2071 | 0,84–0,95 | 2083 | 2053 |
| SE-Alaska, GRACE-ξ fortgesetzt (Oberfläche) | 2035–2084 | 0,89–0,97 | 2095 | 2061 |
| Island, Gletscher SSP5-8.5 (Oberfläche) | 2036–2088 | 0,84–0,95 | 2229 | 2086 |
| Grönland SO, Edwards 95. Perz. | 2070–2118 | 0,85–0,99 | 2195 | – |

**Lesart B:**

- Eine trügerische Ruhe **vor** dem Kippen folgt physikalisch aus dem Modell. Sie setzt 7–60 Jahre
  nach Beginn der Beschleunigung ein.
- Sie ist aber **flach** (4–16 %) und mit heutigen Katalogen frühestens um 2083 statistisch
  erkennbar. In den steilsten Fällen kehrt sie sich (2053–2061) um, bevor sie erkennbar wird.
- Die geodätischen Indikatoren reagieren direkt auf die Last. Sie gehen der seismischen Ruhe voraus.

## B – Heutige Ruhe-Statistik – `quiescence_summary.csv`, `quiescence_etas_windows.csv`, Chart 17

Methoden:

- ETAS wird 1995–2014.5 angepasst und fortgeschrieben (Testfenster 2016–19 und 2020–25).
- Habermann-z vergleicht die entclusterten Jahreszahlen 2020–25 mit 2008–19.

| Region | Habermann-z | ETAS z 2020–26 (beob./erw.) | Artefakt | Last ξ / GNSS | Klasse |
|---|---|---|---|---|---|
| Island (IMO) | +0,19 | −2,4 (0,89) | ja (Magnitudenverschiebung −0,25, KS p < 0,001) | −0,022 / HOFN flach | keine Ruhe (ETAS-only) |
| SE-Alaska (AEC) | **+3,1** (161 → 194/a) | +41 (1,89) | nein | +0,015 n.s. / AB50 ↑ | keine Ruhe (Aktivierung) |
| Grönland (GEUS) | −0,4 | +2,3 | nein | −0,019 / KELY ↑ | keine Ruhe |
| Alpen (SED) | +1,5 | −4,4 (0,77) | nein | – | keine Ruhe (ETAS-only) |
| NZ Südalpen | **−2,5** (109 → 89/a) | −14 (0,61) | nein | – | Ruhe, Lasttrend unbekannt |
| Himalaya-Karakorum | −1,3 | −1,1 | nein | – | keine Ruhe |
| Kontrolle Interior Alaska | −1,3 | −5,0 | nein | – | keine Ruhe (ETAS-only) |
| Kontrolle Nordschweiz | +1,8 | +3,6 | nein | – | keine Ruhe |
| Kontrolle Wellington | −1,3 | −17,8 (0,64) | nein | – | keine Ruhe (ETAS-only) |

**Lesart:**

- **Island zeigt keine Ruhe**, die die Kriterien erfüllt:
  - Die entclusterte Rate ist unverändert.
  - Das ETAS-Signal fällt mit einer Magnitudenverschiebung zusammen (Habermann 1991) und mit dem
    Abklingen der Bárðarbunga-Episode 2014–15 (Sigmundsson et al. 2015).
- **Lastseite Island:**
  - Die Vatnajökull-Massenbilanz verlangsamt sich (ξ < 0), HOFN hebt sich konstant.
  - Das ist das Bild der echten Entspannung bzw. des nordatlantischen Abbremsens (Hugonnet et al. 2021), nicht der trügerischen Ruhe.
- **NZ-Südalpen:**
  - Einzige Ruhe nach der Regel.
  - Die Kontrolle Wellington im selben Netz fällt ebenfalls (Habermann −1,3, ETAS −17,8). Wahrscheinlich ist das ein netz- oder landesweites Muster.
  - Für die Südalpen ist keine GRACE-Box hinterlegt.
- **ETAS-only:** Das Flag schlägt in 2 von 3 Kontrollen an. Deshalb verlangt die Regel die Bestätigung durch Habermann-z.

## CSN Chile (Potin et al. 2024) – `csn_chile_*.csv`

- **Datensatz:** relokalisierter CSN-Katalog 1982 bis Mitte 2020, Box 35–18° S, ≤ 40 km.
  - 39 893 Ereignisse mit Magnitude ab 1990.
  - Mc_ref = 4,0 (wegen der 1990er-Jahre).
  - 2779 entclustert, 1990–2019.
- **F1 (Kontrolle):** keine wachsende saisonale Modulation.
  - b1 = −0,070 ± 0,041 pro Jahrzehnt; Permutation p (zweiseitig) = 0,25.
  - Das ist konsistent mit der ComCat-Kontrolle Central_Andes: +0,016 ± 0,020.
- **Datenlücke:** Im Jahr 2000 liegen in der Box nur 148 Ereignisse.
- **Patagonien deckt der Katalog nicht ab:** südlichster Punkt 45,98° S. Die Aysén-Box (43–46° S)
  hat nur 418 Ereignisse, überwiegend aus 2016–2018, und ist damit nicht nutzbar.

---

# v0.2 (Entwicklungsstand, Branch `v0.2-dev`; Lauf 2026-10-10, Daten bis 2025-12-31)

Regeln: [`../PREREGISTRATION_v0.2.md`](../PREREGISTRATION_v0.2.md) (eingefroren und gepusht **vor**
den Läufen M2/M3). Methoden: [`METHODS_v02.md`](METHODS_v02.md), Prüfung der Schätzer:
[`v02_benchmarks.md`](v02_benchmarks.md). Dateien in `results/v02/`, Charts 18–23.
Explorative (nicht präregistrierte) Zusatzrechnungen sind als solche markiert.
Antwort auf die Reviews zu PR #1: [`reviews/REVIEW_RESPONSE_v0.2.md`](reviews/REVIEW_RESPONSE_v0.2.md).

**Begriff.** µ_y ist die **ETAS-Residual-Hintergrundrate**: der Teil der Rate, den das stationäre
zeitliche ETAS-Modell (tmax 1 a, ohne Raumkern) nicht als Auslösung erklärt. Sie nimmt alles auf,
was das Modell nicht abbildet (Katalog-/Netzänderungen, Schwärme, langsame Transienten, Auslösung
jenseits von 1 a, äußere Spannungen) und ist **keine identifizierte Forcing-Rate**; eine glaziale
Ursache wäre nur eine mögliche Deutung.

**Kurzfassung:** Der präregistrierte Haupttest H2.1 (Trend des ETAS-Hintergrunds SE-Alaska minus
Inner-Alaska) ist formal signifikant, hängt aber vollständig an den Jahren 1995–2002 mit sehr
niedrigen Katalogzahlen in beiden Regionen; ab 2003 bleibt nichts übrig. Keine Region erfüllt
das vorab definierte Kriterium „maskierter Hintergrundanstieg“ (Muster der trügerischen Ruhe);
moderate Effekte sind – besonders in Island und Grönland – nicht ausgeschlossen. Mit der Phase der
modellierten Grad-2-**Körpergezeiten**-Flächendehnung korreliert die Seismizität nirgends
nachweisbar (volle Gezeitenspannung mit Ozeanauflast nicht getestet). Im vereinfachten Lagmodell
verschieben die Sasgen-informierten Parameter das früheste Nachweisjahr in SE-Alaska kaum
(2045,8 → 2047,3).

## M2 / H2.1 – Trend des Hintergrunds 1995–2025 (`m2_etas_background.csv`, `m2_H21_did.csv`, Chart 18)

| Region | Mc | Ereignisse | p (Stufe 1) | Verzw.¹ | Anteil Hintergrund | Trend log µ / Jahrzehnt (SE × 1,25) |
|---|---|---|---|---|---|---|
| **SE_Alaska_AK** | 2,1 | 9 340 | 1,000* | 0,84 | 17 % | **+0,325 ± 0,114** |
| Interior_AK_ctrl | 2,1 | 12 597 | 1,000* | 0,64 | 27 % | −0,079 ± 0,079 |
| NZ_Southern_Alps | 2,8 | 9 366 | 1,000* | 0,87 | 28 % | −0,326 ± 0,059 |
| NZ_Wellington_ctrl | 2,7 | 12 011 | 1,000* | 0,62 | 49 % | −0,421 ± 0,091 |
| Alps_SED | 2,1 | 1 793 | 1,000* | 0,61 | 52 % | −0,349 ± 0,089 |
| N_Switzerland_ctrl | 2,3 | 395 | 1,000* | 0,24 | 79 % | +0,001 ± 0,097 |
| Iceland_Vatnajokull_IMO (beschr.) | 2,5 | 5 732 | 1,065 | 0,90 | 11 % | +0,194 ± 0,144 |
| Greenland_GEUS (beschr.) | 2,7 | 840 | 1,000* | 0,89 | 30 % | +1,047 ± 0,207 |

\* an der Untergrenze 1,0001 (siehe Überraschungen).
¹ Verzweigungsverhältnis **innerhalb des 1-Jahres-Kerns**; bei p ≈ 1 stark vom Cutoff abhängig und
nicht als vollständige Reproduktionszahl eines unbegrenzten ETAS-Prozesses zu lesen.

| Paar (Gletscher − Kontrolle) | Differenz / Jahrzehnt | z | p einseitig | p (BH) |
|---|---|---|---|---|
| **SE_Alaska_AK − Interior_AK_ctrl (primär)** | **+0,405 ± 0,138** | 2,93 | **0,0017** | 0,005 |
| NZ_Southern_Alps − NZ_Wellington_ctrl | +0,095 ± 0,109 | 0,88 | 0,19 | 0,29 |
| Alps_SED − N_Switzerland_ctrl | −0,350 ± 0,132 | −2,66 | 0,996 | 0,996 |

**Nach der Vorab-Regel ist H2.1 für das Primärpaar abgelehnt (Hintergrund in SE-Alaska steigt
stärker als in der Kontrolle).** Die Lesart muss aber vorsichtig sein:

* Chart 18 zeigt den Effekt fast nur in den Jahren 1997–2002: In beiden Alaska-Regionen sinken die
  Katalogzahlen aller Magnituden dort stark (SE-Alaska 1997–2002: 62–196 Beben/Jahr gegenüber
  438–2 059 in 2003–2024; Inner-Alaska 1998–2001: 257–546 gegenüber 654–1 930 ab 2004), das Jahres-Mc (EMR) erreicht 2000 in beiden Regionen
  2,3–2,4 > Mc_ref 2,1. Das spricht für eine Netz-/Katalogphase, die SE-Alaska stärker trifft.
* **Explorativ** (`m2_exploratory_robustness.csv`): nur 2003–2025: Differenz +0,11 ± 0,16
  (z 0,71); ohne 2025: +0,41 ± 0,15 (z 2,82); gemeinsamer Schätzer: +0,43 ± 0,13 (z 3,29), ab 2003
  +0,16 ± 0,14 (z 1,11); p frei (> 0,3): +0,39 ± 0,15 (z 2,56), ab 2003 z 0,34; tmax 3 a:
  +0,23 ± 0,21 (z 1,09), ab 2003 z −1,65.
* **Explorativ, Unsicherheit der Stufe 1** (Review W3, `stage1_propagation_*.csv`): 30 Ziehungen
  von (K, α, c, p) aus der Normalapproximation der Stufe 1, Stufe 2 jeweils neu angepasst (Ziehung
  −1 reproduziert den Produktionswert exakt). Streuung der Trends 0,013 (SE-Alaska) bzw. 0,008
  (Inner-Alaska) pro Jahrzehnt – die SE wachsen dadurch um ≈ 1 % (Fensterverhältnis ≈ 2 %); H2.1-z
  2,93 → 2,90. Einschränkung: p liegt an der Untergrenze 1,0001, dort ist die Normalapproximation
  schlecht (23–27 % der Ziehungen an der Grenze); die Modellunsicherheit (tmax, Startjahr, siehe
  oben) ist viel größer als diese Parameterunsicherheit.
* **Explorativ, Netzänderungen als Störgröße** (`h21_network_models.csv`,
  `h21_network_covariates.csv`; Jahresdifferenz d_y = log µ_SE − log µ_Inner, OLS über 1995–2025).
  Nur der Trend: +0,41 ± 0,09 pro Jahrzehnt (OLS-SE, ohne Faktor). Mit Δ Jahres-Mc als Kovariate:
  +0,39 ± 0,09. Nur Jahre, in denen beide Kataloge bei Mc_ref vollständig sind (28 Jahre): +0,37 ± 0,10.
  Mit Δ log(1 + Stationszahl), aus den FDSN-Metadaten von EarthScope:
  * permanente Netze: +0,38 ± 0,10;
  * alle Netze inkl. temporärer Arrays: **+0,25 ± 0,13** (z ≈ 1,9).

  Die Kovariaten erklären den Trend also nur teilweise. Die Stationszahl ist ein grober Proxy: Die
  FDSN-Metadaten enthalten vor 2000 kaum die damaligen Kurzperioden-Stationen des AEC (SE-Alaska 2
  Stationen 1995–1998). Temporäre Netze speisten den Katalog nicht unbedingt. Das Jahres-Mc
  (MAXC + 0,2) erfasst Lücken in der Vollständigkeit nur grob. Ein Netzartefakt ist damit
  **weder bestätigt noch ausgeschlossen**. Die stärkere Evidenz bleibt der Zusammenbruch des Effekts
  ab 2003 und bei tmax 3 a (siehe oben).
* Fazit: Der präregistrierte H2.1-Test ist formal positiv (die Entscheidungsregel wurde korrekt
  ausgelöst). Der Effekt ist jedoch nicht robust gegen die Beschränkung auf die katalogisch
  homogenere Zeit ab 2003 und gegen einen längeren Triggerhorizont (tmax 3 a). Zusammen mit dem
  zeitvariablen Mc spricht das klar stärker für ein Katalog-/Modellartefakt als für einen glazial
  verursachten Hintergrundtrend; die physikalische Deutung scheitert an einer nicht vorab
  abgesicherten Störgröße. Ein glazialer Beitrag ist damit nicht ausgeschlossen, aber H2.1 liefert
  keinen Beleg dafür.
  Die Präregistrierung verlangte keinen Startjahr-Test – das ist eine Lücke, die C2 (ab 2027,
  homogenes Netz) nicht hat.
* Grönland (+1,05/Jahrzehnt) spiegelt den Netzausbau (GLISN) – nur beschreibend.

## M2 / H2.2 – trügerische Ruhe? (Chart 19)

| Region | µ-Verhältnis 2020–25 / 2008–19 (95 %) | Gesamtverhältnis | Klasse | µ-Verhältnis für 80 % Power² |
|---|---|---|---|---|
| SE_Alaska_AK | 1,41 (1,07–1,85) | 2,33 | Hintergrundanstieg (nicht maskiert) | ≈ 1,5 |
| Interior_AK_ctrl | 0,87 (0,71–1,07) | 0,91 | keine auflösbare Änderung | ≈ 1,3 |
| NZ_Southern_Alps | 0,62 (0,45–0,86) | 0,32 | Hintergrundabnahme (echte Ruhe) | ≈ 1,6 |
| NZ_Wellington_ctrl | 0,99 (0,67–1,47) | 0,71 | keine auflösbare Änderung | ≈ 1,8 |
| Alps_SED | 1,22 (0,96–1,56) | 1,30 | keine auflösbare Änderung | ≈ 1,4 |
| N_Switzerland_ctrl | 1,94 (1,29–2,91) | 2,04 | Hintergrundanstieg (nicht maskiert) | ≈ 1,8 |
| Iceland_Vatnajokull_IMO | 1,56 (0,85–2,86) | 0,19 | keine auflösbare Änderung | ≈ 2,4 |
| Greenland_GEUS | 1,12 (0,75–1,67) | 1,68 | keine auflösbare Änderung | ≈ 1,8 |

² Grobe Näherung exp(2,8·SE_log) aus den berichteten Intervallen (Kriterium „untere 95-%-Grenze
> 1“); ohne Unsicherheit des Gesamtverhältnisses und ohne die Abhängigkeit zwischen µ- und
Rohzählstatistik (beide aus denselben Ereignissen). Vorgeschlagen im Deep-Research-Review.

* **Keine Region erfüllt das vorab definierte Kriterium „maskierter Hintergrundanstieg“.** Das ist
  mäßig informativ gegen große maskierte Anstiege in gut beobachteten Regionen (SE-Alaska ab etwa
  Faktor 1,5), aber keine Evidenz gegen moderate Effekte, in Island und Grönland klar schwach. Die
  Klassifikation ist deskriptiv (Punktschätzer beim Gesamtverhältnis, keine gemeinsame
  Fehlerwahrscheinlichkeit), kein kalibrierter Test. Die v0.1.0-Ruhe in den NZ-Südalpen
  ist im ETAS-Modell eine Abnahme des Residual-Hintergrunds, kein Nachbebenabklingen über
  steigendem Hintergrund. Sie hängt aber am Mc (M1: mit EMR-Mc 3,2 verschwindet sie) und fällt mit
  einem gemeinsamen Sprung beider NZ-Regionen 2012 zusammen (Chart 18) – Netzeffekt wahrscheinlich.
* Island kommt dem Muster am nächsten (Gesamtrate −81 %, µ +56 %), aber das Intervall schließt 1 ein
  und α ≈ 0,02 zeigt, dass ETAS die Schwärme nicht beschreibt.
* SE-Alaska 2025: 2 608 Beben ≥ Mc in einem Jahr (Sequenz); µ_2025 = 83/a liegt im Bereich 2021–2024.

## C2 – eingefrorene Baselines

`results/frozen_v02_baselines.json`, SHA-256 `e2fc568c93622c97607c122c210ed5fcccace0d2440b8cd420fddd931be9f401`
(erzeugt 2026-10-10 aus Daten bis 2025-12-31). SE-Alaska: log µ_ref = 4,05 (µ ≈ 57/a), σ_y = 0,36;
Inner-Alaska: log µ_ref = 4,51 (µ ≈ 91/a), σ_y = 0,16. Die große Jahresstreuung in SE-Alaska macht C2
zum ersten Blick (2029) unempfindlich: grob SE(D) ≈ √(0,36²/3 + 0,36²/10 + 0,16²/3 + 0,16²/10
+ 2·0,1²) ≈ 0,3; die Ablehnungsgrenze (α 0,01) liegt damit bei einem relativen Anstieg um etwa
Faktor 2, für 80 % Power bei etwa Faktor 2,5 (grobe Abschätzung, keine Simulation).

**Offene Punkte vor 2027-01-01 (Review):** Die Präregistrierung ist beim SE-Faktor für C2 nicht
eindeutig (Abschnitt 2 „Modell und Schätzer (H2, C2)“ nennt × 1,25; Abschnitt 5, die JSON-Formel
und `confirmatory_v02.py` enthalten ihn nicht). Außerdem vergleicht C2 ein Mittel jährlicher
log µ_y (Baseline) mit dem log eines gepoolten µ-MLE (Fenster). Beides ist **nicht geändert**;
ein datierter Nachtragsvorschlag und eine explorative Nullsimulation der eingefrorenen
C2-Prozedur stehen in [`PREREG_v0.2_NACHTRAG_BEGRUENDUNG_2026-10-10.md`](PREREG_v0.2_NACHTRAG_BEGRUENDUNG_2026-10-10.md).

## M3 – Körpergezeit (`m3_tides.csv`, Chart 20)

Genau getestet wird die **Korrelation mit der Phase der Grad-2-Körpergezeiten-Flächendehnung**
(skalarer Proxy), nicht „Gezeitenauslösung“ allgemein.

| Region | N (entcl.) | a = 2R/N | Schuster-p | p (BH) | MDE a | Δb (Dehnung − Kompr.) | p einseitig | MDE Δb |
|---|---|---|---|---|---|---|---|---|
| SE_Alaska_AK | 4 517 | 0,042 | 0,14 | 0,54 | 0,068 | +0,023 | 0,79 | 0,066 |
| NZ_Southern_Alps | 3 665 | 0,006 | 0,97 | 0,99 | 0,072 | +0,005 | 0,55 | 0,084 |
| Alps_SED | 1 072 | 0,007 | 0,99 | 0,99 | 0,141 | +0,097 | 0,86 | 0,176 |
| Iceland_Vatnajokull_IMO | 1 227 | 0,071 | 0,22 | 0,54 | 0,126 | −0,007 | 0,46 | 0,149 |
| Greenland_GEUS | 496 | 0,058 | 0,66 | 0,99 | 0,194 | −0,195 | 0,021 | 0,236 |
| Kontrollen (3) | 251–8 542 | 0,006–0,086 | 0,37–0,96 | – | 0,048–0,28 | −0,05…+0,16 | 0,03–0,92 | – |

* Weder H3.1 noch H3.2 ist nach BH signifikant (kleinstes q 0,10, Grönland-b-Wert).
* **Suchfenster (explorativ, Review K1):** Mit dem Code-Standard ±14 h blieben 0,8–2,6 % der Beben
  ohne Phase (SE-Alaska 2,5 %, Island 2,6 %). Neulauf mit ±20 h (`m3_tides_window20.csv`, keine
  Lücken): SE-Alaska Schuster-p 0,14 → 0,19 (a 0,042 → 0,038), Δb-p 0,79 → 0,84; Island 0,22 → 0,28;
  Grönland Schuster-p 0,66 → 0,70, Δb −0,195 → −0,189, p 0,021 → 0,023; kleinstes BH-q (Grönland-b)
  0,10 → 0,12. Keine H3-Aussage ändert sich. Das ±14-h-Fenster war nicht präregistriert.
* Power: In SE-Alaska wäre eine Modulation von ≥ 6,8 % (Rate ∝ 1 + a·cos Phase) mit 80 % Power
  entdeckt worden; beobachtet 4,2 % ± Rauschen. Ein b-Unterschied von ≥ 0,07 wäre sichtbar.
* Die Körpergezeit erreicht an den Bebenorten typisch 20 nstrain (≈ 1–3 kPa). **Ozeanauflast fehlt**,
  ebenso die auf Störungsflächen aufgelöste (Coulomb-)Spannung. Ozeanauflast kann Amplitude und
  Phase lokal deutlich ändern (Tsuruoka et al. 1995 rechneten deshalb Körper- und Ozeangezeit am
  Hypozentrum, doi:10.1111/j.1365-246X.1995.tb03546.x); gerade in SE-Alaska, NZ, Island und
  Grönland. Die MDE gelten nur relativ zur Körpergezeitenphase, nicht für die volle
  Gezeitenspannung; der Nullbefund schließt Auslösung durch die volle Gezeit nicht aus.
* **Ozeanauflast (explorativ, nicht präregistriert; `scripts/v02_m3_ocean_load.py`,
  `m3_tides_ocean_load.csv`):** Auflast-Flächendehnung mit SPOTL (Agnew 1997,
  doi:10.1029/96JB03458) aus TPXO 7.2 (Egbert & Erofeeva 2002), 8 Partialtiden, Orte =
  Bebenschwerpunkte von 0,5°-Zellen; Phase auf Körper- + Auflastgezeit (±20 h). Kontrolle: SPOTLs
  eigene Körpergezeit stimmt mit `tides.areal_strain` überein (Korrelation 0,92–0,999,
  Amplitudenverhältnis 0,92–1,00, kein Zeitversatz).
  * Auflast relativ zur Körpergezeit (RMS): SE-Alaska 19,9 vs. 14,6 nstrain, Grönland 18,8 vs. 11,9,
    NZ-Südalpen 7,0 vs. 18,9, Island 4,6 vs. 12,8, Alpen 1,3 vs. 18,0. Mediane Phasenverschiebung
    19° (SE-Alaska), 71° (Grönland), 8° (NZ), 21° (Island), 5° (Alpen); Anteil der Beben, die die
    Dehnungs-/Kompressionshälfte wechseln: 20 %, 42 %, 8 %, 19 %, 2 %.
  * **Methodischer Befund:** Die Tanaka-Phase ist zu Zufallszeiten nur bei zeitsymmetrischer
    Wellenform gleichverteilt. Mit Auflast ist die Gesamtdehnung asymmetrisch (z. B. längerer
    Anstieg als Abfall), und der einfache Schuster-Test „findet“ dann auch Zufallszeiten (Inner-Alaska
    Schuster-p 5·10⁻⁶, aber Zufallszeiten derselben Orte a = 0,11 bei −78°). Getestet wird deshalb
    gegen die empirische Phasenverteilung zu Zufallszeiten (3 × N Zufallszeiten je Zelle; Statistik
    auf χ²₂, reduziert sich bei Gleichverteilung auf Schuster).
  * Ergebnis (gegen Zufallszeiten, BH über die 5 Gletscherregionen), Körper → Körper + Auflast:
    SE-Alaska p 0,048 → 0,081 (q 0,24 → 0,41; a 0,057 → 0,052); NZ-Südalpen 0,93 → 0,85;
    Alpen 0,84 → 0,87; Island 0,18 → 0,86; Grönland 0,56 → 0,81. b-Wert-Hälften: SE-Alaska
    p 0,84 → 0,075 (Δb +0,03 → −0,04), Grönland 0,023 → 0,58 (Δb −0,19 → +0,02); kleinstes BH-q mit
    Auflast 0,38. **Keine H3-Aussage ändert sich; auch mit Ozeanauflast kein signifikanter Befund.**
    Der knappe Grönland-b-Wert-Effekt der Körpergezeit hängt an der Phasendefinition (42 % der Beben
    wechseln die Hälfte).
  * Die Körpergezeiten-Phasen zu Zufallszeiten sind nahezu gleichverteilt (a 0,007–0,036, im Rahmen
    des Zufallsrauschens der Stichprobe); der eingefrorene H3-/M7-Schuster-Test ist damit nicht
    verzerrt. Für jede Phase auf der vollen Gezeit ist dagegen die Zufallszeit-Referenz nötig.
  * Grenzen: TPXO 7.2 (1/4°) erfasst Fjorde und Küstennähe schlecht (SPOTL meldet Ozeanzellen ohne
    Modellwert, v. a. SE-Alaska); Zellschwerpunkte statt Hypozentren; nur 8 Partialtiden, keine
    langperiodische Auflast; weiterhin keine störungsflächen-aufgelöste Spannung.

## M1 – Katalog-Robustheit (`m1_catalogue_robustness.csv`, Chart 22)

| Region | Mc v0.1 / EMR | F1 β1 v0.1 | GK | EMR-Mc | Habermann-z v0.1 / GK / EMR |
|---|---|---|---|---|---|
| SE_Alaska_AK | 2,1 / 2,1 | +0,035 ± 0,023 | +0,050 ± 0,023 (Perm.-p 0,01) | = v0.1 | +3,1 / +3,4 / +3,1 |
| Interior_AK_ctrl | 2,1 / 1,9 | −0,005 ± 0,019 | +0,012 ± 0,020 | −0,031 ± 0,018 | −1,3 / +0,3 / −1,1 |
| NZ_Southern_Alps | 2,8 / 3,2 | +0,038 ± 0,023 | +0,055 ± 0,028 (p 0,016) | +0,021 ± 0,036 | **−2,5 / −2,3 / −0,4** |
| NZ_Wellington_ctrl | 2,7 / 3,2 | −0,008 ± 0,015 | −0,002 ± 0,022 | −0,037 ± 0,027 | −1,3 / −0,8 / −0,6 |
| Alps_SED | 2,1 / 2,2 | +0,058 ± 0,039 | +0,061 ± 0,036 | +0,061 ± 0,045 | +1,5 / +2,2 / +0,8 |
| N_Switzerland_ctrl | 2,3 / 2,4 | +0,092 ± 0,073 | +0,047 ± 0,066 | (N < 300) | +1,8 / +3,1 / +1,9 |
| Iceland_Vatnajokull_IMO | 2,5 / 3,9 | −0,096 ± 0,063 | −0,135 ± 0,090 | (N = 44) | +0,2 / **−3,1** / +2,5 |
| Greenland_GEUS | 2,7 / 3,8 | +0,146 ± 0,087 | +0,140 ± 0,081 | (N = 47) | −0,4 / +0,6 / +2,5 |

* F1 in SE-Alaska ist robust gegenüber der Entclusterung (GK etwas stärker, Perm.-p 0,01
  unkorrigiert, explorativ). Mc-Bootstrap: Standardabweichung ≤ 0,05 (MAXC) bzw. 0,0–0,07 (EMR)
  außer Grönland (0,13).
* Die Ruhe-Einstufung der NZ-Südalpen aus v0.1.0 hängt am Mc; die Island-Ruhe unter GK am
  Entclusterungsverfahren (Schwärme). Beides relativiert v0.1.0-Monitoring M5 und wird so berichtet;
  M5 selbst bleibt unverändert eingefroren.
* EMR-Referenz-Mc ist in Island/Grönland/NZ viel höher, weil die Jahreswerte der dünnen frühen
  Jahre das 90-%-Quantil bestimmen; dort ist F1 mit EMR-Mc nicht prüfbar.

## M4 – Lag-Modell mit Sasgen et al. 2026 (`m4_lag_*.csv`, `m4_eta_scan*.csv`, Chart 21)

Genauer: **Dünnplatten-/Halbraum-Sensitivität, angelehnt an Sasgen et al. 2026** – keine
Reproduktion der Sasgen-Rheologie. Sasgen et al. rechnen mit VILMA (selbstgravitierend,
Maxwell-viskoelastisch, vier Schichten: elastische Lithosphäre, Asthenosphäre bis 400 km, oberer
Restmantel 5e20, unterer Mantel 3e21 Pa·s). Hier wird ihre Lithosphärendicke als effektive
elastische Dicke Te und ihre Asthenosphärenviskosität als Halbraumviskosität eingesetzt – beides
Modellannahmen, keine Parametertransformationen.

| Variante | SE-Alaska τ (λ 300 km) | Kompensation C | frühestes Nachweisjahr Oberfläche / GRACE | Island τ (λ 200 km) | Island Oberfläche / GRACE |
|---|---|---|---|---|---|
| v0.1.0 (η 1,4e19, Te 60; Island 8e18, Te 15) | 64 a | 0,11 | **2045,8** / 2061,3 | 302 a | 2070,3 / 2183,3 |
| **Sasgen bevorzugt (Alaska 3e18, Te 30; Island 1e18, Te 30)** | 62 a | 0,50 | **2047,3** / 2064,8 | 10 a | 2062,3 / 2107,3 |
| nur η (Te wie v0.1.0) | 14 a | 0,11 | 2045,8 / 2060,8 | 38 a | 2063,3 / 2118,3 |
| Island GNSS LT 40 km | – | – | – | 4,7 a | 2061,8 / 2106,3 |
| Ensemble-Obergrenze (3e19, Te 90) | 44 a | 0,04 | 2045,8 / 2060,8 | 13 a | 2061,8 / 2106,3 |

* η-Scan 10¹⁸–10²⁰ Pa·s (SE-Alaska, Oberfläche): Te 60 km → 2045,8–2046,3; Te 30 km → 2046,3–2050,8.
* Lesart (Eigenschaft des Szenariomodells, keine geophysikalische Feststellung über Alaska): Das
  Modell teilt die Antwort per Konstruktion in einen sofortigen Kanal (1 − C) und einen mit τ
  verzögerten Kanal (C); C ist ein flexuraler Kompensationsfaktor, dessen Gleichsetzung mit dem
  verzögerten Anteil der Coulomb-Spannung eine zusätzliche Annahme ist. Te ändert zugleich C und
  τ (τ = τ_Halbraum·C). Im Modell hängt das früheste Nachweisjahr in SE-Alaska daher fast nur an
  (1 − C), kaum an der Viskosität. Niedrigere Viskosität verkürzt τ (64 → 14 a bei gleichem Te),
  ändert aber das Nachweisjahr nicht; die dünnere Platte (Te 30 km) macht mehr der Antwort viskos
  und verschiebt es leicht nach hinten. Für Island verkürzt sich τ von ~300 auf ~10 Jahre und das
  früheste Nachweisjahr rückt um ~8 Jahre vor (2070 → 2062).
* Seismizitätsverhältnis geförderter Störungen 2100 (Maximum über Szenarien): SE-Alaska 2,35 → 2,19;
  Island 1,99 → 2,50.

## Überraschungen

1. **p an der Untergrenze:** In 7 von 8 Regionen läuft der Omori-Exponent der stationären Stufe auf
   1,0001; Verzweigungsverhältnisse (im 1-a-Kern) 0,6–0,9, Hintergrundanteil teils < 20 %. Das ist
   ein ernstes Diagnosezeichen (Fehlanpassung durch Raum-Heterogenität, Schwärme oder Katalogeffekte
   wird durch einen langen Zeitschwanz kompensiert). Bei p = 1 enthält das erste Jahr nur rund
   79 % der Omori-Masse von 5 Jahren (Beispiel c = 0,002 a); Auslösung jenseits von 1 a landet im
   Hintergrund oder bei jüngeren Auslösern. Niveaus und – wie tmax 3 a für Alaska zeigt – auch
   Trends sind daher modellabhängig. Eine explorative Nullsimulation im Randregime steht im
   Nachtragsentwurf.
2. **H2.1 formal positiv, aber nicht robust** (siehe oben) – ein Lehrstück dafür, dass ein
   präregistrierter Test ohne Startjahr-Prüfung an einer Netzphase hängen kann.
3. **NZ-Ruhe** aus v0.1.0: im ETAS-Hintergrund echt, aber Mc-abhängig und netzweit (Sprung 2012).

## English summary (v0.2 development run)

Preregistered H2.1 (ETAS background trend, SE Alaska minus Interior Alaska): +0.41 ± 0.14 per decade,
z = 2.93, p = 0.0017 (BH 0.005) – the preregistered decision rule fired, but the effect is not robust
to starting in 2003 (+0.11 ± 0.16, exploratory) or to a 3-yr triggering horizon; together with the
time-varying Mc this points to a catalogue/model artefact rather than a glacially driven background
trend. mu_y is the ETAS *residual* background (whatever the stationary temporal ETAS does not
explain), not an identified forcing rate. No region meets the predefined "masked background rise"
(deceptive-quiet) criterion; moderate effects are not excluded, especially in Iceland/Greenland; the v0.1.0 NZ Southern Alps quiet is a genuine
background decrease in the ETAS model but is Mc-dependent and network-wide. No significant correlation with the
phase of the degree-2 body-tide areal strain (Schuster, b-value; BH); SE Alaska MDE 6.8 % modulation
relative to that phase, Δb 0.07. Exploratory ocean loading (SPOTL, TPXO 7.2) changes the phases
substantially in SE Alaska and Greenland, but tested against the empirical phase distribution at random
times (needed because the total-strain waveform is time-asymmetric) nothing becomes significant
(smallest BH q 0.38); fault-resolved stress is still not modelled. Exploratory network covariates
explain part, not all, of the H2.1 trend (0.41 → 0.25–0.39 per decade); a network artefact is neither
confirmed nor excluded. The recovery study re-run with the corrected simulator is qualitatively
unchanged. Thin-plate/half-space lag sensitivity informed by Sasgen et al. 2026: SE
Alaska earliest detection 2045.8 → 2047.3 (within this reduced model governed by the instantaneous
fraction 1 − C rather than viscosity – a property of the model architecture); Iceland τ ~300 → ~10 yr, earliest detection 2070 → 2062.
C2 baselines frozen (SHA-256 e2fc568c…). Surprise: Omori p hits its lower bound almost everywhere.
