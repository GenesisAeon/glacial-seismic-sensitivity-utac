# Faktencheck: Gemini-Deep-Research-Bericht für das v0.3-Modul „Massenänderung und Kollaps“

Stand: 2026-10-11 (Abrufe zwischen ca. 10:30 und 12:00 MESZ). Geprüft wurde gegen Primärquellen (Crossref, DataCite, Verlags- und Repositoriumsseiten), gegen die USGS-ComCat-FDSN-Schnittstelle und gegen Nachrichtenquellen zum Budhi-Gandaki-Ereignis.
Geprüfte Datei: `Mass_Change_Induced_Seismicity.md`, im Repo unverändert als [`raw/gemini_deepresearch_v0.3_mass_change.md`](raw/gemini_deepresearch_v0.3_mass_change.md) (103 KB, deutsch, 102 Referenzen). Der Bericht beruht auf unserem Prompt `docs/GEMINI_DEEPRESEARCH_PROMPT_v0.3.md` (Branch `v0.3-dev`, ae8cd0b). Formelsymbole liegen nur als eingebettete Bilder vor; die zahlentragenden Bilder (u. a. 0,09/kPa, c = 0,5, B = 0,6, ~23 ± 1 Gt/a, 2500 ± 1700 MW) wurden dekodiert und mitgeprüft.

**Urteilsskala:** korrekt · ungenau · falsch · nicht prüfbar · halluziniert. Der Zusatz **[Framing]** markiert eine Überzeichnung durch die Wortwahl, die über die Quelle hinausgeht.

## Kennzahlen

| Größe | Wert |
|---|---|
| Referenzen im Bericht | 102, fast nur URLs. Nur 2 enthalten eine DOI (Ref. 11 Columbia Academic Commons, Ref. 101 Frontiers); beide lösen auf. |
| URL-Status (curl, Browser-UA) | 78 × erreichbar (76 × HTTP 200, 2 × 202), 20 × 403 (v. a. ResearchGate, OUP/GJI, MDPI, CDC; blockt nur den automatischen Abruf), 1 × 429, 3 × Timeout bzw. keine Verbindung. Keine URL zeigt auf eine nicht existierende Arbeit. |
| DOIs geprüft | 32 eindeutige DOIs. Abgedeckt sind die beiden aus dem Bericht und 30, die wir den wissenschaftlich tragenden Referenzen zugeordnet haben (Crossref-Suche nach Titel und Autor). Alle 32 lösen auf: 29 über Crossref, 3 über DataCite. Liste in Abschnitt C. |
| Geprüfte Aussagen | 48 (Tabelle A) |
| Urteile | **26 korrekt (davon 3 mit falscher Quellenzuordnung) · 14 ungenau · 4 falsch · 3 nicht prüfbar · 1 halluziniert** |
| Fehlerquote | 5 von 48 (10 %) sind falsch oder halluziniert. Rechnet man die ungenauen Aussagen hinzu, sind 19 von 48 (40 %) nicht ohne Korrektur übernehmbar. |
| Quellen-Zuordnungsfehler | Mindestens 8 Aussagen sind mit einer unpassenden Referenz belegt (Details in Abschnitt B). |

## Gesamturteil

- **Keine erfundenen Fachartikel.** Alle wissenschaftlichen Referenzen existieren. Die harten Zahlen zu Lorca, Bingham Canyon, Sasgen 2026, Pine Island und den Skaftá-Jökulhlaups stimmen weitgehend mit den Quellen überein.
- **Überzeichnung bei den Schlussfolgerungen.** Beispiele sind „exzellenter Beweis“ (Lorca), „faktisch ausgeschlossen“ (ISO-Anteil) und „Initiator tektonischer Seismizität“ (Bingham). Die Synthese (§7) behauptet, das Budhi-Gandaki-Ereignis zeige, dass Erdrutsche Erdbeben auslösen. Für dieses Ereignis gibt es aber keinen seismischen Befund: ComCat führt am 9.–12.10.2026 im Gebiet weder ein Erdbeben noch eine Rutschung.
- **Das Ausgabeformat des Prompts wurde ignoriert.** Es fehlen die Unsicherheitslabels (established/reported/speculative), die gerankte Kalibrierliste und die Tabellen B/C. DOIs fehlen fast vollständig, und der Bericht ist auf Deutsch statt Englisch.
- **Große inhaltliche Lücken.** Nicht behandelt werden die ausdrücklich angefragten Fälle Punggye-ri 2017, Bárðarbunga 2014–15 und Koyna–Warna, außerdem Gashydrate, Karst, Permafrost und das Langtang-Ereignis vom 26.08.2026. Letzteres taucht nur indirekt als Datenkatalog in Ref. 96 auf. Genau für den Kern des Moduls, den Kollaps über einem Hohlraum, liefert der Bericht also kaum Material.
- **Wiederholter Fehler aus dem v0.2-Bericht.** Der b-Wert-Effekt von ~0,09 pro kPa aus Tan et al. 2019 (Axial Seamount) wird erneut verallgemeinert.
- **Die Quellenqualität ist gemischt.** Neben Primärarbeiten stehen Wikipedia (Ref. 7, 14), ResearchGate- und Scribd-Kopien, Software-Marketingseiten (Ref. 98, 100: MCP-Server-Listings) und ein Artefakt („Google Sports Data“, Ref. 46).

## A. Inhaltliche Behauptungen

| # | Behauptung (Gemini, Abschnitt) | Urteil | korrekte Quelle | Anmerkung |
|---|---|---|---|---|
| 1 | Lorca: Mw 5.1 am 11.05.2011 (§3.1) | korrekt | González et al. 2012, *Nat. Geosci.* 5:821, https://doi.org/10.1038/ngeo1610 | – |
| 2 | Lorca: 9 Todesopfer (§3.1) | korrekt | Ref. 14 (Wikipedia); allgemein dokumentiert | Nur Sekundärquelle zitiert. |
| 3 | Grundwasserspiegel zwischen den 1960ern und 2010 um ≥ 250 m gefallen (§3.1) | korrekt | González 2012 | „at least 250 m“ |
| 4 | Grundwasserbedingte Subsidenz „etwa 2 cm pro Jahr“ (§3.1) | **falsch** | González 2012, Fig. 1 und Text | Das Alto-Guadalentín-Becken senkt sich um **> 10 cm/Jahr**. 2 cm/Jahr ist nur die Konturlinie der Karte. |
| 5 | Bruch in 1–5 km Tiefe (§3.1, Tab. 1) | ungenau | González 2012 | Das Paper nennt Slip „at very shallow depths of 2–4 km“ (Modell ~1 bis ~4 km entlang des Einfallens). „1–5 km“ vermischt mehrere Angaben. |
| 6 | Streichen N225°E, revers + linkslateral, max. Slip ~15 cm (§3.1) | korrekt | González 2012 | – |
| 7 | AMF-Sliprate 0,07–0,6 mm/a, Slip-Defizit seit 1818 von 1,4–12 cm (§3.1) | korrekt | González 2012 | – |
| 8 | Reibung c = 0,5, Skempton B = 0,6 (§3.1) | korrekt | González 2012, Supplement | – |
| 9 | Lorca als „exzellenter Beweis“, dass Wasserentnahme ein jahrhundertealtes Defizit „katastrophal freisetzt“ (§3.1) | ungenau [Framing] | González 2012 | Die Autoren zeigen eine räumliche Übereinstimmung zwischen Entlastungs-ΔCFS und Slip. Das ist ein Einzelfall-Argument, kein Beweis. |
| 10 | Groningen: Förderbeginn 1963 (§3.2) | korrekt | van Thienen-Visser & Breunese 2015, *TLE* 34:664, https://doi.org/10.1190/tle34060664.1 | Osinga et al. 2026 (Ref. 18) nennt 1965; in der Literatur kommen beide Jahreszahlen vor. |
| 11 | Erstes Ereignis ML 2.4 im Jahr 1991 (§3.2) | korrekt | van Thienen-Visser & Breunese 2015; Osinga 2026 („since 1991“) | – |
| 12 | ~5 Ereignisse pro Jahr (ML ≥ 1,5?) konstant bis 2003, danach Kopplung von Förderung, Senkung und Rate (§3.2) | nicht prüfbar | Ref. 20 (ResearchGate, gesperrt) | Plausibel; der Volltext war nicht abrufbar. Die Magnitudenschwelle ist nur als Bild angegeben. |
| 13 | Mmax „bis zu 6.4“, berechnet von „Bourne oder van Thienen-Visser“ (§3.2, Tab. 1) | ungenau | Bourne et al. 2017, *NJG* 96:s175, https://doi.org/10.1017/njg.2017.35 (Ref. 21) | 6,4 ist eine **einzelne** Schätzung aus der gesamten Volumenänderung des Reservoirs (Bourne et al. 2014). Der Expert-Workshop 2016 setzte dagegen eine Verteilung an. Zitiert ist die falsche Referenz (19 statt 21). |
| 14 | Kompaktionsmechanismus mit Ref. 18 belegt (§3.2) | ungenau | Osinga et al. 2026, *NHESS* 26:3443, https://doi.org/10.5194/nhess-26-3443-2026 | Ref. 18 behandelt **Gasinjektion** (Druckerhaltung) und deren Risiko, nicht primär die Kompaktion. Nützlich ist der dort zitierte Code: TNO-Hazard-Risk-Modelle, https://doi.org/10.5281/zenodo.21239992. |
| 15 | In Salah: KB-502, InSAR-Hebung, Mikroseismizität, thermoelastische Abkühlung fördert Reaktivierung (§3.3) | nicht prüfbar | Ref. 2, 3, 26 | Im Kern Literaturkonsens, aber nicht im Detail geprüft. Für v0.3 hat der Fall geringe Priorität (Treiber: Injektion, keine Massenabnahme). |
| 16 | Crandall Canyon: 6.8.2007, ML 3.9 (§3.4, Tab. 1) | korrekt | Pechmann et al. 2008, *SRL* 79:620, https://doi.org/10.1785/gssrl.79.5.620 | Zitiert sind Ref. 28 (ANF-Bulletin) und 30. Die Primärquelle fehlt. |
| 17 | Crandall Canyon: Momententensor dominant implosiv, Hohlraumkollaps (§3.4) | korrekt (Zuordnung falsch) | Dreger et al. 2008, *Science* 321:217, https://doi.org/10.1126/science.1157392 | Gemini belegt das mit Dahm et al. (Ref. 30), einer allgemeinen Diskriminierungs-Empfehlung. Dreger 2008 findet zusätzlich eine kleinere **Nicht-Kollaps-Komponente**. |
| 18 | Dominanter implosiver ISO-Anteil schließt ein tektonisches Beben „faktisch aus“ (§5.1) | **falsch** | Dreger 2008; Dahm et al. 2013, *J. Seismol.* 17:197, https://doi.org/10.1007/s10950-012-9295-6 | Dreger schreibt vorsichtig, der MT „may be used for source-type discrimination“. Der ISO-Anteil flacher Quellen ist schlecht aufgelöst (Trade-off mit CLVD, Oberflächeneffekte). Implosive Anteile gibt es auch bei natürlichen Vulkan- und Calderaprozessen. Bei Dahm et al. ist der Mechanismus nur ein Kriterium unter mehreren. |
| 19 | Hoher NDC-Anteil ist ein „extrem starkes Indiz“ für eine anthropogene oder fluide Quelle (§5.1) | ungenau [Framing] | Dahm 2013 | NDC tritt auch natürlich auf (vulkanisch, geothermal, komplexe Brüche). Der Anteil ist ein Indiz, kein starkes Einzelkriterium. |
| 20 | Netze zeichnen Hohlraumveränderungen „in Echtzeit“ geometrisch auf (§3.4) | ungenau [Framing] | – | MT-Inversionen sind nachträgliche Analysen, kein Echtzeitprodukt. |
| 21 | Bingham Canyon: 10.4.2013, Grube 970 m tief, zwei Abgänge von je ~90 s im Abstand von ~1,5 h, ~65 Mio. m³ (§3.4) | korrekt | Pankow et al. 2014, *GSA Today* 24(1):4, https://doi.org/10.1130/GSATG191A.1 | 65 Mio. m³ ist das **Ablagerungsvolumen**; das Quellvolumen beträgt ~55 Mio. m³. |
| 22 | ML 2.5/2.4, md > 3.5; die Diskrepanz ist typisch für Rutschungsquellen (§3.4) | korrekt | Pankow 2014 | md = 4,2 bzw. ≥ 3,5. Ms 5,1/4,9 (Ekström) nennt Gemini nicht. |
| 23 | 16 Folgeereignisse in 6 Tagen, md −0,8 bis 3,0 (§3.4) | korrekt | Pankow 2014 | Das Paper selbst nennt an einer Stelle „ten days“. |
| 24 | Die statische Laständerung durch die Rutschung „triggerte 16 tektonische Folgebeben“; die Rutschung sei „Initiator tektonischer Seismizität“ (§3.4, Tab. 1, §7) | ungenau [Framing] | Pankow 2014 | Die Autoren schreiben „it appears that … the landslide triggered small earthquakes“ und lassen den Mechanismus ausdrücklich als offene Frage stehen. |
| 25 | Budhi Gandaki: Ereignis am 11.10.2026 im nördlichen Gorkha, vor Sonnenaufgang (§3.5) | korrekt | Kathmandu Post 11.10.2026; The Statesman 11.10.2026 | Laut Anwohnern Geräusche ab ~4 Uhr NPT, Anstieg des Pegels ~4:30 Uhr. |
| 26 | Ursache: Ein Erdrutsch in Chumchet (Chumnubri-6) blockierte den Budhi Gandaki bzw. den Syar, danach Dammbruch (§3.5) | ungenau | Kathmandu Post (DHM), Onlinekhabar, Farsight, Reuters/Business Recorder | Die Ursache ist **nicht bestätigt**. Genannt werden drei Varianten: Blockade des Syar zwischen Lokpa und Chumling, ein Rutsch im Ungilung Khola (linker Zufluss des Syar) und eine von Anwohnern vermutete Lawine am Shringi (unbestätigt). Laut DHM zeigt ein Satellitenbild einen großen Rutsch, wohl vom Vortag. Gemini stellt eine Arbeitshypothese als Tatsache dar. |
| 27 | Mehr als 35 Häuser, mehrere Brücken und das Baulager des 341-MW-Projekts (70 Mrd. NPR) weggespült (§3.5) | korrekt | The Statesman; Kathmandu Post („35 to 40 houses“); Farsight | Stand: vorläufige Meldungen vom 11.10. |
| 28 | Vier Vermisste aus einer Hütte am Ungilung (§3.5) | ungenau | The Statesman (4); Kathmandu Post (bis zu 5, dazu 4–5 Hirten ohne Kontakt); Farsight (≥ 10) | Die Zahlen widersprechen sich noch; Gemini nennt nur eine Variante. |
| 29 | Das Ereignis wird als GLOF bzw. Gletschersee-Ausbruch eingeordnet (§3.5) | **falsch** | wie 26 | Gemeldet ist ein Erdrutschdamm; eine Gletscherseebeteiligung ist nicht belegt. Gemini verwechselt das möglicherweise mit dem Langtang-Ereignis vom 26.08.2026. |
| 30 | Die Flut erzeugt „starke seismische Oberflächenwellen“ und kann „Flankenkollapse und flache Seismizität induzieren“ (§3.5) | **halluziniert** | – | Gemini gibt keine Quelle an. ComCat (Abfrage vom 11.10., Ereignistypen earthquake und landslide, 27,5–29,5° N, 83,5–86° E, 9.–12.10.) liefert **0 Ereignisse**. Die Aussage ist als Befund zum Ereignis formuliert, aber durch nichts gedeckt. |
| 31 | Budhi Gandaki belegt, dass gewaltige Erdrutsche Erdbeben triggern (§7) | **falsch** | wie 30 | Für dieses Ereignis gibt es keine Seismizität. |
| 32 | Dieterich 1994: Ratengesetz mit Zustandsvariable; Abklingzeit t_a = Aσ/τ̇ (§2.2) | korrekt | Dieterich 1994, *JGR* 99:2601, https://doi.org/10.1029/93JB02581; Heimisson & Segall 2018, https://doi.org/10.1029/2018JB015656 | Zitiert wird die Revision von 2018 statt des Originals. |
| 33 | RSF: Bei hochfrequenter zyklischer Last wird die Rate „unabhängig von Periode und Rate“ (§2.2) | ungenau | Colledge et al., ESS Open Archive, https://doi.org/10.1002/essoar.10512456.1 (Ref. 10) | Die Theorie sagt für Perioden ≪ t_a eine Modulation proportional zu Δτ/(Aσ) voraus, ohne Periodenabhängigkeit. „Unabhängig von der Rate“ ist zu pauschal; nicht im Detail geprüft. |
| 34 | b-Wert sinkt um ~0,09 pro kPa ΔCFS; Phasen hoher Gezeitenspannung erhöhen „selektiv“ die Wahrscheinlichkeit zerstörerischer Beben (§2.3) | ungenau [Framing] | Tan et al. 2019, *EPSL*, https://doi.org/10.1016/j.epsl.2019.01.047 | Die Zahl stimmt, gilt aber nur für Axial Seamount und erst oberhalb einer Schwelle. Derselbe Übertragungsfehler stand schon im v0.2-Bericht (Faktencheck v0.2, Nr. 5/6). |
| 35 | Gezeitenphase 0° = Peak, ±180° = Tal (§2.3) | korrekt | Standarddefinition (z. B. Tan 2019) | – |
| 36 | Sasgen 2026: Die GIA-Korrektur beträgt in Alaska ~23 ± 1 Gt/a (davon ~7 GIA_PD), in Island ~6 ± 1 Gt/a. Der Eisverlust steigt dadurch in Island um ~32 % und in Alaska um ~9 % (AV = 3·10¹⁸ Pa s, LT = 30 km) (§4.1) | korrekt | Sasgen et al. 2026, *Commun. Earth Environ.* 7:518, https://doi.org/10.1038/s43247-026-03738-y | Für Island verwendet das Paper AV = 1·10¹⁸ Pa s. Daten: Harvard Dataverse (Replikationsdaten). |
| 37 | Die schnelle Entlastung „fördert Dekompressionsschmelzen“ und vulkanotektonische Seismizität unter den Eiskappen (§4.1) | nicht prüfbar | – | Steht nicht in Sasgen 2026. Als Hypothese aus anderer Literatur plausibel, hier aber unbelegt. |
| 38 | Pine Island: δ³He bis 12,2 % gegenüber 9,15 % (CDW); Wärme 2500 ± 1700 MW (§4.1) | korrekt | Loose et al. 2018, *Nat. Commun.* 9:2431, https://doi.org/10.1038/s41467-018-04421-3 | „Massive“ Wärmequelle ist Framing; die Autoren schreiben von etwa der Hälfte von Grímsvötn. |
| 39 | Jökulhlaups: 50 bis > 3000 m³/s, 0,05–0,4 km³ (§4.2) | korrekt | Eibl et al. 2020, *Nat. Commun.* 11:2504, https://doi.org/10.1038/s41467-020-15744-5 | – |
| 40 | Tremor „primär“ bei 1,4–3,2 Hz (bzw. 1,5–10 Hz) (§4.2) | ungenau | Eibl 2020 | 1,4–3,2 Hz ist das **Filterband** der Array-Analyse. Typ-2-Tremor reicht bis 7 Hz. |
| 41 | Typ 1 folgt der Flutfront, Typ 2 besteht aus Raumwellen und korreliert mit dem Einsturz des Kesseldachs (§4.2) | ungenau | Eibl 2020 | Typ 1 und die Raumwellen sind belegt. Für Typ 2 diskutieren die Autoren mögliche Ursachen, legen sich aber nicht auf den Einsturz fest. |
| 42 | Vorwarnzeit 20–34 h; 2011 lagen nur 50 min zwischen Warnung und Erreichen der Ringstraße (§4.2) | korrekt | Eibl 2020 | – |
| 43 | Fjallsárlón: Sonar 420 kHz (2020), Schallgeschwindigkeit 4 m/s pro °C (§4.2) | korrekt | Wells et al. 2025, *NHESS* 25:1913, https://doi.org/10.5194/nhess-25-1913-2025 | Für das Seismizitätsmodul ohne Belang. |
| 44 | Ogata & Katsura 1993: Mc-Modell mit Normal-CDF-Detektionsfunktion (§5.2) | korrekt | *GJI* 113:727, https://doi.org/10.1111/j.1365-246X.1993.tb04663.x | – |
| 45 | Nichtstationäres ETAS mit μ(t), K(t), Glättung und ABIC, „Kumazawa & Ogata (2013)“ (§5.3) | korrekt | Kumazawa & Ogata 2014, *Ann. Appl. Stat.* 8:1825, https://doi.org/10.1214/14-AOAS759 (Ref. 56) | Die zitierte Arbeit stammt von 2014. Eine JGR-Arbeit derselben Autoren von 2013 existiert ebenfalls. |
| 46 | Grond: BABO, L1-Norm, probabilistische Zentroid-MT-Inversion (§6.1) | korrekt (Zuordnung falsch) | Heimann et al. 2018, GFZ Data Services, https://doi.org/10.5880/GFZ.2.1.2018.003 | Gemini belegt Grond mit Mancuso et al. 2025 (*GJI*, Ref. 70), einer Anwendungsstudie zu den Liparischen Inseln. Grond ist offen (GPL-3, git.pyrocko.org). |
| 47 | LiCSBAS lädt Interferogramme „vom Copernicus SciHub“ (§6.2) | ungenau | Morishita et al. 2020, *Remote Sens.* 12:424, https://doi.org/10.3390/rs12030424 | LiCSBAS nutzt vorprozessierte **COMET-LiCSAR**-Produkte. SciHub wurde 2023 durch den Copernicus Data Space ersetzt. Lizenzen geprüft: LiCSBAS GPL-3, MintPy GPL-3, ISCE2/ISCE3 Apache-2.0. |
| 48 | ComCat-API ohne Schlüssel, GeoJSON/FDSN, libcomcat (§6.3) | korrekt (Zuordnung falsch) | USGS FDSN Event Web Service (eigene Abfrage am 11.10. ohne Schlüssel erfolgreich) | Belegt mit Ref. 96 (Nepal-Datenkatalog), 98/100 (MCP-Server-Listings) und 99 (TexNet). Das Repo `usgs/libcomcat` auf GitHub ist **archiviert**; aktiv ist code.usgs.gov/ghsc/esi/libcomcat-python. |

## B. Quellen-Auffälligkeiten

- **Ref. 46 „Google Sports Data“** führt auf eine Google-Hilfeseite zum Knowledge Graph. Das ist ein Artefakt, keine Quelle.
- **Ref. 7 und 14** sind Wikipedia-Artikel.
- **Ref. 98 und 100** sind Listings eines MCP-Servers (GitHub, LobeHub). Fachlich taugen sie nicht als Beleg.
- **Ref. 96** ist der echte offene Datenkatalog zur Kaskade vom 26.08.2026 in Nepal (Liaskos et al., Zenodo, https://doi.org/10.5281/zenodo.23034746, DataCite geprüft). Gemini nutzt ihn aber als Beleg für die ComCat-API.
- **Ref. 101** (HotLINK, Vulkan-Hotspots in Alaska) steht ohne Bezug in §6.3.
- **Ref. 51** ist ein AGU-Abstract von 2018 (Eibl et al.), keine begutachtete Arbeit.
- **Ref. 28, 30 und 70** sind für Crandall Canyon bzw. Grond falsch zugeordnet (siehe A 16, 17, 46).
- **Ref. 19 und 21** sind bei Mmax vertauscht (siehe A 13).

## C. Aufgelöste DOIs (32, alle auflösbar)

Crossref: 10.1038/ngeo1610 · 10.1029/2018JB015656 · 10.1029/93JB02581 · 10.1002/essoar.10512456.1 · 10.1016/j.epsl.2019.01.047 · 10.5194/nhess-26-3443-2026 · 10.1190/tle34060664.1 · 10.1017/njg.2017.35 · 10.1007/s10950-012-9295-6 · 10.1126/science.1157392 · 10.1785/gssrl.79.5.620 · 10.1130/GSATG191A.1 · 10.1038/s43247-026-03738-y · 10.1038/s41467-018-04421-3 · 10.1038/s41467-020-15744-5 · 10.5194/nhess-25-1913-2025 · 10.1785/0120250144 · 10.1111/j.1365-246X.1993.tb04663.x · 10.1785/BSSA0640051363 · 10.1214/14-AOAS759 · 10.1093/gji/ggad370 · 10.1016/j.cageo.2007.07.005 · 10.1093/gji/ggaf532 · 10.3390/rs12030424 · 10.3390/rs12152430 · 10.1016/j.cageo.2019.104331 · 10.31223/osf.io/9sz6m · 10.3389/feart.2024.1345104
DataCite: 10.5281/zenodo.21239992 · 10.5880/GFZ.2.1.2018.003 · 10.7916/D8ZS36QP · 10.5281/zenodo.23034746

## D. Nicht geliefert, obwohl angefragt

- **Fälle:** Punggye-ri 2017 (Kollaps nach dem Test), Bárðarbunga 2014–15 (Calderaeinbruch), Koyna–Warna (Stausee), Langtang (2015 und 26.08.2026). Diese Fälle müssen wir selbst recherchieren.
- **Ungenannte Treiber:** Gashydrat-Dissoziation, Karst und Erdfälle, Permafrost-Degradation, Salzkavernen.
- **Format:** Es fehlen die gerankte Kalibrierliste mit Datensätzen, Effektgrößen (ΔCFS, Zeitskalen) in Tabellenform, die Labels established/reported/speculative und die Diskriminator-Tabelle mit Trennschärfe je Merkmal.

## E. Zusatzbefund aus der eigenen Prüfung (nicht von Gemini)

- **USGS ComCat führt zwei als „landslide“ typisierte Ereignisse am 26.08.2026 im Langtang-Gebiet** (Abfrage vom 11.10.2026):
  - `us7000tbwb`, 02:52:10 UTC (= 04:52 MESZ), Ms_vx 5,2, Tiefe 0 km, 28,271° N / 85,515° E;
  - `us7000tc90`, 06:00:35 UTC (= 08:00 MESZ), Ms_vx 4,2.
  Damit liegt ein offen katalogisierter Massenbewegungsfall mit seismischer Quelle vor. Er ist der wichtigste neue Kalibrierkandidat aus diesem Durchgang. Ein Sekundärbericht nennt eine anfängliche Einstufung als M 4,4-Erdbeben; das haben wir nicht selbst geprüft.
- **Für Budhi Gandaki (11.10.2026) gibt es bislang keinen ComCat-Eintrag** (siehe A 30).
