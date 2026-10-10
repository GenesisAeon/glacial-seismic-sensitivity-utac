# Grenzen – was ausgeschlossen ist und was offen bleibt

## Was die Daten ausschließen (im Rahmen der Power)

- **Starker Anstieg der saisonalen Empfindlichkeit:** In SE-Alaska (AEC, M ≥ 2,1) hat sich die saisonale Modulation 1990–2025 **nicht** um mehr als ~0,08 pro Jahrzehnt erhöht (obere 95-%-KI-Grenze von β1).
  - Das ist eine Aussage über **kleine bis mittlere Beben, die saisonal reagieren**, nicht über einzelne große Brüche.
  - Für die Empfindlichkeit pro kPa (γ1) ist die obere 95-%-Grenze ≈ +0,009 pro kPa und Jahrzehnt.
- **Gletscherspezifischer Trend in den Kritikalitätsindikatoren:** 16 von 544 Einzeltests sind nach BH-Korrektur signifikant, aber überwiegend Netz-/Mc-, b-Wert- und Varianzeffekte, 4 davon in Kontrollregionen. Kein Gruppenvergleich Gletscher vs. Kontrolle ist signifikant (0 von 180), AR1 und Erholungsrate nirgends. Details in [`RESULTS.md`](RESULTS.md).

## Was die Daten nicht ausschließen

- **Verzögerte viskose Antworten** über Jahrzehnte bis Jahrtausende (Lag-Modell). Über Ratentrends sind sie mit heutigen Katalogen praktisch nicht nachweisbar.
- **Einzelne große Beben** auf kritisch gespannten Verwerfungen (Pärvie-, Fairweather-artig). Zählstatistik kleiner Beben sagt darüber wenig.
- **Moderates Empfindlichkeitswachstum** unterhalb der Nachweisgrenze. Der finale konfirmatorische Look 2036 hat für den retrospektiven Punktschätzer nur ~50 % Power.
- **Effekte in Regionen ohne brauchbaren Katalog:** Westantarktis, Patagonien (zu dünn), Himalaya unterhalb M 4,7.
- **Vulkanische Effekte** (Dekompressionsschmelzen). Sie sind nicht Gegenstand der Tests.

## Methodische Grenzen

1. **Retrospektiv ≠ präregistriert:** Die Tests 1990–2025 berühren Daten, die in Phase 2 explorativ gesehen wurden. Nur C1 (ab 2026-11-01) ist sauber präregistriert.
2. **Saisonale Detektionsartefakte:** Jahres-Fixed-Effects beseitigen Netzstufen, aber keine *saisonal* schwankende Detektion (Sturmrauschen, Meereis, Stationen nur im Sommer).
   - Wir arbeiten konservativ über Mc_ref und prüfen Mc nach Monat. Die Kontrollregionen desselben Netzes sind die wichtigste Absicherung.
   - Grönland (GEUS) ist hier am verdächtigsten: November-Mc 2,4, wenige Daten vor ~2008.
3. **Regen vs. Eis nicht trennbar** (SE-Alaska): GRACE-Entlastung und ERA5-Regen- bzw. Schneeanomalien korrelieren mit r ≈ 0,68.
   - Die QAIC-Unterschiede sind klein, die Koeffizienten im gemeinsamen Modell instabil.
   - GRACE misst *Gesamtmasse* (Schnee, Eis, Grundwasser), also kein reines „Eis“-Signal.
4. **GRACE-Auflösung:** Mascons haben ~1°, die regionalen Mittel verschmieren die Last. Die Empfindlichkeit „pro kPa“ ist deshalb pro *regional gemitteltem* kPa zu lesen.
   - Die Übereinstimmung mit Johnson et al. 2020 (3,5 %/kPa, modellierte Spannung) ist teils Zufall der Normierung.
   - Vatnajökull hat nur einen Mascon.
5. **Declustering:** Die NN-Methode mit festen Parametern (d_f = 1,6, b = 1) ist eine Wahl. ETAS-Declustering wäre eine Alternative (nicht umgesetzt).
6. **Mehrfachtests:** BH je Testfamilie. Die Gruppen-Meta-Analysen sind explorativ, weil sich Regionen innerhalb eines Tiers teils überlappen und die Kontrollen heterogen sind.
7. **Lag-Modell:** κ ist unbestimmt, λ angenommen, Halbraum + Platte, keine 3-D-Viskosität. Ergebnisse sind Größenordnungen. Details in [`LAG_MODEL.md`](LAG_MODEL.md).
8. **Kausalität:** Eine Korrelation von Seismizität und Last ist kein Beweis für eine Last-Ursache, denn hydrologische Prozesse sind miteinander verkoppelt.

## Zusätzliche Grenzen der Erweiterungen (v0.1.0)

9. **Kippszenarien (A):** Es sind skalierte Pfade, keine Projektionen. Die Faktoren m(2100) stammen aus dem Integral einer angenommenen Exponentialkurve, das auf die publizierten Meeresspiegelbeiträge (Edwards et al. 2021) bzw. die „Größenordnung schneller“-Aussage (DeConto et al. 2021) normiert ist.
   - κ ist unbekannt. Ein Kipppunkt wird nicht modelliert, nur seine Wirkung auf die Entlastungsrate.
   - Nach 2100 wird die Rate konstant gehalten.
   - Gebirgsgletscher verlieren in Wirklichkeit Fläche. Ihre Entlastung kann also nicht unbegrenzt wachsen.
10. **Trügerische Ruhe (B):** Der Schattenanteil f = 0,6 ist eine Annahme. Bei f < 0,5 entsteht keine Netto-Ruhe.
    - Echte Störungsgeometrien und Spannungsfelder fehlen.
    - Aseismisches Kriechen und Porendruck-Drainage (vgl. die effiziente subglaziale Entwässerung bei Sundal et al. 2011 und Tedstone et al. 2015 als Analogie) sind nur als Hypothesen genannt, nicht modelliert.
11. **Quieszenz-Statistik:** Das zeitliche ETAS ohne Raumkern unterschätzt die Überdispersion. Große frühere Sequenzen (Kaikōura 2016, Bárðarbunga 2014–15) verzerren die Fortschreibung.
    - Habermann-z setzt eine stationäre Hintergrundrate voraus.
    - Beide Statistiken sind Flags, keine p-Werte.
12. **Geodäsie:** ξ hängt vom Zeitfenster ab. Kurzfristige Schwankungen (z. B. NAO, Bevis et al. 2019) können ein Flag auslösen oder verdecken.
    - GNSS-Beschleunigungen enthalten elastische Antworten auf Laständerungen und lokale Effekte.
    - Sprünge werden nur an NGL-gelisteten Daten modelliert.

## Ergänzung v0.2

* Das ETAS-Hintergrundmodell ist rein zeitlich, mit tmax = 1 Jahr; der Omori-Exponent landet fast
  überall an der Untergrenze. µ-Niveaus sind modellabhängig, Trends und Verhältnisse weniger.
* H2.1 kann – wie gezeigt – an einer Netzphase hängen (1995–2002 in Alaska). Netzinterne Kontrollen
  helfen nur, wenn die Netzänderung beide Regionen gleich trifft.
* Gezeiten: nur Körpergezeit, keine Ozeanauflast; ein Nullbefund schließt Gezeitenauslösung durch
  die volle Gezeit nicht aus.
* Lag-Modell: Die Lithosphärendicke aus GIA-Modellen (Sasgen et al. 2026) wird als elastische Dicke
  eines Plattenfilters verwendet; Viskositäten aus Alaska/Island werden auf Halbraum-Relaxation
  übertragen. Ergebnisse sind Szenarien, keine Vorhersagen.
* µ_y ist ein ETAS-Residual-Hintergrund, keine identifizierte Forcing-Rate (Netz, Schwärme,
  Produktivitätsänderungen, Auslösung jenseits 1 a landen ebenfalls darin). Verzweigungsverhältnisse
  gelten nur innerhalb des 1-a-Kerns.
* H2.2 ist eine deskriptive Klassifikation ohne kalibrierte Fehlerwahrscheinlichkeit; der Nullbefund
  schließt nur große maskierte Anstiege in gut beobachteten Regionen aus (SE-Alaska ab ≈ Faktor 1,5),
  in Island/Grönland erst ab ≈ 1,8–2,4.
* C2 ist ein bedingter Test unter dem eingefrorenen ETAS-Modell (Unsicherheit von K, α, c, p nicht
  enthalten; p an der Untergrenze). Er schützt nicht gegen differentielle Netzänderungen ab 2027.
* Die Gemini-Recherche, die v0.2 anregte, ist keine Quelle; zitiert werden nur Originalarbeiten.
