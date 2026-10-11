# v0.3 S2 – Explorative Kalibrierung und regelbasierter Diskriminator

**Status:** EXPLORATIV und datenberührt. Alle Schwellen wurden an genau diesen Daten gewählt. Die Trefferquoten unten sind deshalb **keine** Gütemaße, sondern eine Plausibilitätsprüfung (Zirkularität, kleines n). Eine belastbare Prüfung ist erst prospektiv nach dem S3-Einfrieren möglich (M8).

- **Code:** `src/.../v03_features.py`, `src/.../v03_discriminator.py`, `scripts/v03_s2_calibration.py`
- **Ausgaben:** `results/v03/s2_*`

## Regeln (Reihenfolge; die erste zutreffende Regel gilt)

| Regel | Klasse | Bedingung |
|---|---|---|
| L0 | laut Label | Katalogtyp `landslide`, `mine collapse` oder `collapse` (nur Modus „full“) |
| R1 | mass_movement | publizierte langperiodische Einzelkraft-Inversion, **oder** Tiefe ≤ 1 km und M_lang − M_kurz ≥ 0,8 |
| R2 | collapse | publizierte MT-Klasse implosiv bzw. schließender Riss, **oder** voller Katalog-MT mit ISO-Anteil ≤ −0,3 bei Tiefe ≤ 1 km, **oder** Tiefe ≤ 1 km und ein größeres Ereignis ≤ 15 km in der Stunde davor |
| R4 | caldera_collapse | ≥ 10 Ereignisse mit M ≥ 4,5 im Umkreis von 15 km und ±0,5 Jahren, **und** Median-DC der ComCat-MTs ≤ 46 % bei mindestens 3 Tensoren |
| – | tectonic | sonst |

Das ISO-Vorzeichen ist absichtlich **keine** allgemeine Kollapsregel. Punggye-ri ist keine reine Implosion, Napoleonville zeigt Volumen*zunahme*, und Bárðarbunga ist überwiegend aseismisch. R2-mt erfasst nur implosive Kollapse.

## Kalibrierung an 659 tektonischen Kontroll-Hauptbeben (M ≥ 4,5, 2000–2026)

| Schwelle | Kontrollverteilung | gewählt |
|---|---|---|
| dm_min (M_lang − M_kurz) | n = 91; Median 0,19; q99 0,67; Max 0,71 | 0,8 (Untergrenze a priori 0,8) |
| dc_max (Median-DC im Cluster) | n = 42 Cluster mit ≥ 3 MTs; Median 84,6 %; q01 47,1 % | 46 % |
| n_m45_min | q99 32, Max 77 (Gorkha-Nachbeben) | 10 (a priori). Die Clusterzahl allein trennt nicht; erst die DC-Bedingung trennt. |
| iso_max | 18 Kontrollen mit nicht-deviatorischem MT, alle mit \|ISO\| ≤ 0,003 | −0,3 (gewählt **nach** Sichtung von Crandall: −0,46) |

Die Kontrollen sind ungleich verteilt: 455 Nepal (überwiegend Gorkha-Sequenz), 158 Island, 26 Korea/NO-China, 12 SE-Spanien, je 4 Utah und W-Indien. Nur 1 Kontrolle liegt in ≤ 1 km Tiefe, 69 haben ein größeres Ereignis in der Stunde davor.

## Ergebnis (Ereignisebene: 42 Schlüsselereignisse der 8 Fälle, davon 33 Bárðarbunga-Ereignisse mit M ≥ 5)

| Modus | Fälle richtig (Mehrheit) | nicht-tektonische Fälle erkannt | Fehlalarme Kontrollen |
|---|---|---|---|
| full (Label + Katalog + publiziert) | 8/8 | 5/5 | 1/659 |
| no_labels (Katalog + publiziert) | 7/8 | 4/5 (Langtang verfehlt) | 1/659 |
| catalogue_only | 6/8 | 3/5 (Bingham fehlt im Katalog; Langtang verfehlt) | 1/659 |

- **Crandall:** Im Modus „catalogue_only“ wird der Fall über R2-mt erkannt. Der UUSS-Voll-MT in ComCat hat ISO −0,46 und 6 % DC; die Regel wurde nach Sichtung gewählt.
- **Punggye-ri:** über R2 erkannt (Tiefe 0, Explosion 8,5 min vorher).
- **Bárðarbunga:** 33/33 über R4 (Median-DC der Cluster 14–33 %).
- **Lorca, Koyna, Groningen:** werden korrekt als tektonisch eingestuft. Die Forcing-Achse ist nicht getestet: Lorca braucht keine Daten (Literatur), für Koyna und Groningen fehlt die Forcing-Zeitreihe.
- **Langtang:** Ohne Label nicht erkennbar. ComCat führt nur Ms_vx (Tiefe 0) und keine zweite Magnitude, also fehlt die Diskrepanz.
- **Bingham:** Die beiden Rutschungen fehlen in ComCat. Nur mit publizierten Werten (ML 2,5/2,4 gegenüber md > 3,5, LP-Kraftinversion) wird der Fall erkannt.
- **Einziger Fehlalarm:** Kontrolle `usb000t124` (Island, 2014-11-29, M 4,5) liegt 26 km vom Calderazentrum entfernt und damit knapp außerhalb des in S0 festgelegten 25-km-Ausschlusses. Physikalisch gehört sie zur Bárðarbunga-Episode. Formal zählt sie als Fehlalarm.

## Groningen (beschreibend, `s2_groningen_annual.csv`)
- **Raten (ML ≥ 1,5):**
  - ~5/Jahr in 1993–2002 (passt zur Angabe im Faktencheck)
  - Höchstwerte 26–27/Jahr in 2011 und 2013
  - 2016–2022 11–17/Jahr
  - 2023–2025 7–9/Jahr; 2026 bis September 4
- **Größtes Ereignis:** Huizinge, 2012-08-16, ML 3,6 (`knmi2012qcdh`).
- **Auch nach Förderende:** 2025-11-14 ML 3,4 bei Zeerijp (`knmi2025whfa`).
- **b-Wert (Mc 1,5):** 0,90 ± 0,05 (1995–2013, n = 208) und 0,85 ± 0,06 (2014–2022, n = 137), kein signifikanter Unterschied. Für 2023–2026 ist n = 27 zu klein.
- **Einschränkung:** Der 30-km-Kreis kann auch Ereignisse aus Nachbarfeldern enthalten. Die Kopplung an die Förderung ist ohne Förderzeitreihe nicht prüfbar.

## Nicht gemacht
- Eigene MT-Inversion: optional und nicht machbar ohne Wellenform-Pipeline (obspy fehlt, kein GPU-Bedarf, aber erheblicher Aufwand).
- Nichtstationäres ETAS für Groningen: zurückgestellt, bis die Förderdaten geklärt sind.
- InSAR: wie vereinbart erst in einer späteren Version.
