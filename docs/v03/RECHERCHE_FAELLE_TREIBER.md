# v0.3 – Eigene Recherche: Zusatzfälle und offene Treiber

Stand: 2026-10-11. Alle DOIs wurden über die Crossref-API aufgelöst (Liste mit Titel und Prüfzeit: `drivers/verified_dois.tsv`). Die Aussagen unten stammen aus den Abstracts bzw. frei zugänglichen Volltexten der genannten Arbeiten oder direkt aus USGS ComCat (Abfrage 2026-10-11). Der Gemini-Bericht ist hier keine Quelle.

## 1. Zusatzfälle (Ränge 6–8)

### Punggye-ri 2017 (Rang 6, Klasse `collapse`)
- ComCat: `us2000aert` (03:30:01 UTC, M 6.3, Typ „nuclear explosion“) und `us2000aetk` (03:38:31 UTC, M 4.1, Typ „collapse“), beide mit fester Tiefe 0 km.
- Chiang et al. 2018, SRL, https://doi.org/10.1785/0220180130: mb 6.1 für den Test, mb 4.1 für das Ereignis 8,5 min später. Der Momententensor des Kollapses ist **keine reine Implosion**, sondern passt zu einem schließenden Zugriss mit zweiseitiger vertikaler Punktkraft.
- Alvizuri & Tape 2018, SRL, https://doi.org/10.1785/0220180158: volle MT-Analyse der DPRK-Tests.
- **Bewertung:** geeignet. Sauber gelabelt und publizierte MT-Klasse. Der Fall zeigt aber, dass „Kollaps = negatives ISO“ zu einfach ist.

### Bárðarbunga 2014–15 (Rang 7, Klasse `caldera_collapse`)
- Gudmundsson et al. 2016, Science, https://doi.org/10.1126/science.aaf8988: Die Caldera sank über 110 km² um 65 m ab, allmählich und nahezu exponentiell abklingend über ~180 Tage. Ursache war der Magmaentzug aus ~12 km Tiefe über einen 48 km langen Gang.
- Riel et al. 2015, GJI, https://doi.org/10.1093/gji/ggv157: Die Randbeben haben **stark nicht-double-couple** Mechanismen. Der Großteil der Absenkung lief **aseismisch** ab.
- Ágústsdóttir et al. 2016, GRL, https://doi.org/10.1002/2015GL067423: Die Gangseismizität ist Blattverschiebung; der Gang selbst öffnete aseismisch. Gangbeben gehören also **nicht** zur Kollapsklasse.
- Sigmundsson et al. 2015, Nature, https://doi.org/10.1038/nature14111: segmentiertes laterales Gangwachstum.
- ComCat: 241 Ereignisse M ≥ 4 und 36 mit M ≥ 5 innerhalb von 15 km um die Caldera (08/2014–03/2015); Mww-Lösungen vorhanden.
- **Bewertung:** geeignet als Referenz für die Klasse „wiederholte M ≥ 4,5 mit großem Nicht-DC-Anteil“.

### Koyna–Warna (Rang 8, Klasse `tectonic` mit Stausee-Forcing, eingeschränkt)
- Gupta 2002, Earth-Sci. Rev., https://doi.org/10.1016/S0012-8252(02)00063-6, und Gupta 2022, J. Earth Syst. Sci., https://doi.org/10.1007/s12040-021-01780-2: Übersichten zur stauseegetriggerten Seismizität mit Schwerpunkt Koyna.
- ComCat/ISC-GEM: `iscgem828259`, 1967-12-10 22:51 UTC, M 6.54 (Tiefe fest 10 km).
- **Einschränkung:** Es gibt keine offene Pegelzeitreihe, und ComCat ist für M < 4 unvollständig. Der Forcing-Test entfällt; der Fall dient nur als Negativfall (tektonische Quelle) für den Diskriminator.

### Optional vorgeschlagen (Entscheidung nötig, nicht in S0)
- **Napoleonville 2012 (Salzkaverne, Erdfall)** – Nayak & Dreger 2014, BSSA, https://doi.org/10.1785/0120130260: 62 Ereignisse Mw 1,3–1,6 mit großen **Volumenzunahme**-Anteilen (61–82 %), also nicht implosiv. Daten nur aus lokalem Netz.
- **Kīlauea 2018 (Calderakollaps)** – Shelly & Thelen 2019, GRL, https://doi.org/10.1029/2019GL085636: wiederholte Kollapsereignisse mit Mw ~5; Deutung als gekoppelte Scherung plus Rissschließung. Neal et al. 2019, Science, https://doi.org/10.1126/science.aav7046.

## 2. Kernfälle: Ergänzungen zur Verifikation

- **Crandall Canyon 2007:**
  - ComCat führt `uu50342430` als „mine collapse“ (ML 3.93, Tiefe −2,5 km).
  - ML 3,9 laut Ford et al. 2008 (https://doi.org/10.1785/gssrl.79.5.637); Mw 4,1 laut Kubacki et al. 2014 (https://doi.org/10.1002/2014JB011037).
  - Dreger et al. 2008 (https://doi.org/10.1126/science.1157392): implosiv dominiert, plus kleinere Nicht-Kollaps-Komponente.
  - Kubacki 2014: In den 48 h vor dem Kollaps änderten sich b-Wert und Lage der Ereignisse; dafür war Template-Matching bis Mc 0,0 nötig.
- **Bingham Canyon 2013 (auffällig):**
  - Laut Pankow et al. 2014 (GSA Today, https://doi.org/10.1130/GSATG191A.1) hatten die beiden Rutschungen die Herdzeiten **03:30:22 und 05:05:22 UTC**, ML 2,5 und 2,4 und md > 3,5. In den 6 Tagen danach folgten 16 tektonisch aussehende Ereignisse.
  - **Die beiden Rutschungen selbst stehen nicht als Ereignisse in ComCat.** Die ComCat-Einträge um 03:43 und 05:16 UTC passen zeitlich nicht zu den Herdzeiten und sind als „earthquake“ typisiert.
  - Folge: Für Bingham kommen die Merkmale des Schlüsselereignisses aus der Publikation, nicht aus dem Katalog.
  - Weitere Quellen: Hibert et al. 2014 (https://doi.org/10.1002/2014GL060592; Kraftinversion) und Moore et al. 2017 (https://doi.org/10.1002/2016JF004036; 52 Mm³).
- **Langtang 2026:** In ComCat stehen zwei „landslide“-Ereignisse, `us7000tbwb` (Ms_vx 5,2, Tiefe 0) und `us7000tc90` (Ms_vx 4,2). Begutachtete Literatur gibt es noch nicht.
- **Groningen:** KNMI-FDSN liefert die Ereignisse mit EventType „induced or triggered event“; das erste Ereignis ist 1991-12-05, ML 2,4, Middelstum. Quellen: van Thienen-Visser & Breunese 2015 (https://doi.org/10.1190/tle34060664.1) und Dost et al. 2017 (https://doi.org/10.1017/njg.2017.20).
- **Lorca 2011:** ComCat `usp000j1en` (M 5,1, Tiefe 1 km) und Vorbeben `usp000j1ea` (M 4,5, 1 h 42 min vorher). González et al. 2012 (https://doi.org/10.1038/ngeo1610): Die Verteilung des Versatzes wird durch Grundwasserentlastung gesteuert.

## 3. Offene Treiberthemen (für das Register)

| Thema | Register-ID | Ergebnis | Quellen |
|---|---|---|---|
| Gashydrate | D-HYD | spekulativ; heutige Effekte gering, kein Seismizitätsbezug belegt | Maslin et al. 2010, https://doi.org/10.1098/rsta.2010.0065; Ruppel & Kessler 2017, https://doi.org/10.1002/2016RG000534 |
| Karst / Erdfälle | D-KARST | Geogefahr etabliert; kein katalogtauglicher seismischer Fall gefunden | Gutiérrez et al. 2014, https://doi.org/10.1016/j.earscirev.2014.08.002 |
| Permafrost | D-PERMA | Felsinstabilität berichtet; wirkt über Massenbewegungen (D-SLIDE) | Krautblatter et al. 2013, https://doi.org/10.1002/esp.3374; Gruber & Haeberli 2007, https://doi.org/10.1029/2006JF000547 |
| Salzkavernen | D-SALT | berichtet; MT bei Napoleonville mit Volumenzunahme | Nayak & Dreger 2014, https://doi.org/10.1785/0120130260; Mercerat et al. 2009, https://doi.org/10.1007/s00024-009-0008-1 |

Zusätzlich aufgenommen: D-CALD (Calderakollaps), D-RES (Stausee) und D-INJ. D-INJ ist selbst belegt mit Ellsworth 2013, https://doi.org/10.1126/science.1225942.

**Bei der Prüfung aufgefallen:** Zwei DOIs, die ich aus dem Gedächtnis angesetzt hatte, gehörten zu fremden Arbeiten: 10.1098/rsta.2009.0245 und 10.1016/j.earscirev.2013.08.007. Beide wurden vor der Aufnahme per Crossref-Suche ersetzt. Das bestätigt die Regel, dass nur aufgelöste DOIs ins Register dürfen; der Test `tests/test_v03_drivers.py` erzwingt das.
