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
