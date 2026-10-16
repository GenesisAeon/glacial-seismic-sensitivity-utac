# Antwort auf das Gemini-Gutachten zum Preprint P133 (Entwurf v0.2.1)

**Rohfassung:** `docs/reviews/raw/gemini_paper_review_v0.2.1.md`. Gemini ist Gutachter und Ideenquelle, keine wissenschaftliche Quelle.

**Prüfung (2026-10-15):**
- Jede Behauptung wurde gegen `paper/P133_preprint.tex`, den Code und `results/*.csv` geprüft.
- Jede vorgeschlagene Literatur wurde über Crossref geprüft (DOI, Titel, Jahr). Wo nötig wurden Abstract oder Volltext gelesen: Sasgen 2026, Pankow 2014, Tan 2019, Eibl 2020.

**Änderungen am Paper:** Commit `89a8c6d` auf `paper-v0.2.1`. Eingefrorene Präregistrierungsdateien und Ergebnisse sind unverändert.

**Empfehlung des Gutachtens:** keine formale Empfehlung. Inhaltlich entspricht sie „Major Revision / im aktuellen Design abzulehnen“: Sechs „zwingende Auflagen“ werden genannt, die „Early-stage tests“ seien „wertlos“.

**Gesamturteil:** Das Gutachten ist überwiegend generisch.
- Viele Kritikpunkte beschreiben Dinge, die das Paper bereits enthält:
  - GIA- und viskoelastisches Modell (F5, Sasgen-Lauf M4);
  - Rate-and-State nach Dieterich;
  - Nearest-Neighbour-Declustering statt Gardner–Knopoff;
  - Gezeitenphase nach Tanaka;
  - Porendruck.
- Mehrere Forderungen sprengen den Umfang (InSAR-Pipeline, PyLith, MT-Inversion).
- Der UTAC-Vorwurf trifft auf das Paper nicht zu.
- Brauchbar sind einige Präzisierungen; sie wurden übernommen.

## Zählung

| Einstufung | Anzahl |
|---|---|
| gültiger Fehler | 1 |
| berechtigter Vorschlag | 12 (6 umgesetzt, 3 als künftige Arbeit benannt, 1 bereits im Text, 2 abgelehnt wegen Umfang) |
| falsch | 9 |
| nicht prüfbar | 2 |
| halluziniert | 1 |

**Zitate:** Alle 30 geprüften Literaturhinweise existieren (DOIs siehe unten), keiner ist erfunden. Einige Belege sind jedoch keine zitierfähigen Quellen: Wikipedia, ResearchGate, Scribd, sorah.io und ein GitHub-Repo „earthquake-mcp-server“.

## Punkt für Punkt

| # | Punkt (Gemini) | Einstufung | Prüfung und Antwort | Änderung |
|---|---|---|---|---|
| 1 | GIA und viskoelastische Relaxation werden ignoriert; das Paper nehme elastischen, linearen Spannungstransfer an. | falsch | Die Einleitung behandelt GIA; F5 ist ein Platten-Halbraum-Modell mit Relaxationszeiten; M4 ist ein Sensitivitätslauf nach Sasgen et al. (2026). Grenzen sind in den Limitations genannt. | – |
| 2 | Sasgen et al. 2026: Die Eisverlust-Korrektur verändere die Eingangsrate „um Größenordnungen“. | berechtigter Vorschlag (Fakt korrekt, Schluss falsch) | Laut Abstract (DOI 10.1038/s43247-026-03738-y) beträgt der zusätzliche Verlust etwa 7 ± 1 Gt/a in Alaska (etwa 9 %) und etwa 3 ± 1 Gt/a in Island (etwa ein Drittel). Das ist keine Größenordnung. | Limitation ergänzt: Folgen für trendbasierte Lasten (Lag- und Kipp-Szenarien, M1), geringere für die saisonale Last in F2. |
| 3 | Dreidimensionale Maxwell-Modelle und PyLith seien Pflicht. | berechtigter Vorschlag, künftige Arbeit | PyLith ist real (Aagaard et al. 2013, 10.1002/jgrb.50217; Walker et al. 2023, 10.1093/gji/ggad370). Für ein Paper mit oberen Schranken ist das zu viel Umfang. | Als nächster Schritt unter „What remains open“ genannt. |
| 4 | Anthropogene Analogien (Lorca, Groningen) zur Kalibrierung heranziehen. | berechtigter Vorschlag, künftige Arbeit | Quellen verifiziert: González et al. 2012 (10.1038/ngeo1610), van Thienen-Visser & Breunese 2015 (10.1190/tle34060664.1), Bourne et al. 2014 (10.1002/2014JB011663). Eine Übertragung der Spannungskoeffizienten wäre eine neue Analyse. Lorca und Groningen sind bereits v0.3-Fälle. | – |
| 5 | Rate-and-State fehle; „Sensitivität“ bleibe beschreibend. | falsch | Dieterich (1994) wird in den Methods (F5, Kipp-Modell) zitiert, die Discussion leitet die Skalierung ΔS/(TṠ) her. | Zitat zusätzlich in der Discussion gesetzt (nur Klarheit). |
| 6 | Weniger Normalspannung verkleinere das kritische Nukleationsvolumen. | falsch | Bei Rate-and-State gilt für die kritische Nukleationslänge L_c ∝ G·d_c/((b−a)·σ). Sinkt σ, **wächst** L_c. | – |
| 7 | Forcing und Sensitivität werden nicht unterschieden. | **gültiger Fehler** (Definition fehlte) | Die Discussion streift das Thema, aber eine Definition fehlte. F1 und C1 können wachsendes Forcing nicht von wachsender Sensitivität trennen; F2 normiert auf die Last. | Definition in der Einleitung ergänzt, einschließlich der Grenze von F1 und C1. |
| 8 | Instationäres ETAS kann überanpassen; ML-Diagnostik nötig. | berechtigter Vorschlag, teilweise schon adressiert | Petrillo & Dal Zilio 2026 existiert (EPSL, 10.1016/j.epsl.2026.120308). Das Paper hat bereits eine Nullkalibrierung (Faktor 1,25), Startjahr- und Netz-Kovariaten-Checks und deutet H2.1 deshalb als Artefakt. | – (künftige Arbeit) |
| 9a | Mc nach MAXC sei „fahrlässig“; die Detektion schwanke saisonal. | berechtigter Vorschlag (Ton überzogen) | Verwendet wird MAXC + 0,2, Referenz ist das 90-%-Quantil der Jahreswerte, dazu EMR und Bootstrap. Die monatlichen Mc lagen in `results/seasonal_mc_by_month.csv` vor, standen aber nicht im Paper. | Satz ergänzt: Monats-Mc ≤ Mc_ref in allen Regionen außer SE-Alaska im Dezember (2,2 statt 2,1). Ogata & Katsura (1993) als nicht angewandte Alternative genannt. |
| 9b | MAXC unterschätze Mc um bis zu 0,8 Einheiten. | nicht prüfbar | Quelle ist eine chinesische Zeitschriftenseite ohne geprüfte DOI; die Zahl stammt aus einem Spezialfall. Woessner & Wiemer (2005) ist der Grund für die Korrektur +0,2. | – |
| 10 | Gardner–Knopoff-Declustering sei ungeeignet. | falsch | Hauptverfahren ist Zaliapin & Ben-Zion (2013). Gardner–Knopoff dient nur als Alternative und für die globale Basislinie. Zitat verifiziert: 10.1785/BSSA0640051363. | – |
| 11 | Gezeitenphase nach Tanaka et al. (2002) präzisieren. | falsch | Genau so umgesetzt: Methods 3.5, Love-Zahlen eingefroren. | – |
| 12 | Gezeitenspannung auf Störungsflächen projizieren. | berechtigter Vorschlag, bereits im Text | Steht in Results und Limitations („no fault-resolved stress“). | – |
| 13 | Schwelle der Spannungsamplitude für die b-Wert-Abhängigkeit (Tan et al. 2019). | berechtigter Vorschlag (Fakt verifiziert) | Tan et al. 2019 (10.1016/j.epsl.2019.01.047, bereits zitiert): oberhalb etwa 5 kPa ändert sich b um etwa 0,03 je kPa Vertikalspannung bzw. etwa 0,09 je kPa Coulomb-Spannung; der Gezeitenhub dort beträgt ±20 kPa. Eine neue Hypothese wäre neuer Umfang. | Satz ergänzt: Körpergezeiten in unseren Regionen liegen bei etwa 1 kPa oder darunter; ein Null-Ergebnis für H3.2 war erwartbar. |
| 14 | MDEs unterstellten unabhängige, gleich verteilte Daten. | berechtigter Vorschlag (teilweise falsch) | F1 und C1 rechnen mit der beobachteten Quasi-Poisson-Überdispersion φ (`power.py`) auf declusterten Ereignissen. Für Restclustering gilt der Einwand. | Limitation ergänzt. |
| 15 | Benjamini–Hochberg setzt Unabhängigkeit bzw. PRDS voraus. | berechtigter Vorschlag | Für Regionen in verschiedenen Netzen ist das plausibel. Eine Korrektur für beliebige Abhängigkeit (Benjamini–Yekutieli) würde die q-Werte nur erhöhen; kein Null-Ergebnis würde sich ändern. | Satz in Methods 3.2 ergänzt. |
| 16 | Kryoseismik und Jökulhlaup-Tremor können die Kataloge kontaminieren. | berechtigter Vorschlag | Eibl et al. 2020 verifiziert (10.1038/s41467-020-15744-5). Bisher wurde nur nach Ereignistyp „earthquake“ gefiltert (`fetch/catalogs.py`); das stand nicht im Paper. | Data-Satz und Limitation ergänzt; Eibl 2020 im Literaturverzeichnis. |
| 16b | Tremor im Band 1,5–10 Hz | nicht prüfbar | Die Frequenzangabe steht nicht im Abstract; der Volltext wurde nicht geprüft. Sie wird nicht übernommen. | – |
| 17 | ComCat sei „oft nur auf M > 2,5 bzw. 4,5 gefiltert“. | falsch | ComCat enthält alle Magnitudenstufen; M2.5+ und M4.5+ sind nur Feed-Zusammenfassungen. Die Hauptregionen nutzen ohnehin nationale Kataloge. Quelle ist sorah.io, nicht zitierfähig. | – |
| 18 | Bingham Canyon: nicht-DC-Quelle, „16 echte tektonische Beben in 10 Tagen“. | falsch bzw. überzogen | Pankow et al. 2014 (10.1130/GSATG191A.1): ML 2,5/2,4 und md > 3,5 sind richtig. Die 16 Ereignisse beschreiben die Autoren aber nur als „possibly triggered“ mit Wellenformen „characteristic of tectonic earthquakes“; eine nicht-DC-Quelle wird dort nicht genannt. Für v0.2.1 nicht relevant (Thema von v0.3). | – |
| 19 | Momenttensor-Inversion mit ISOLA oder Grond sei Pflicht. | berechtigter Vorschlag, abgelehnt (Umfang) | Sokos & Zahradník 2008 verifiziert (10.1016/j.cageo.2007.07.005). Die v0.3-Präregistrierung schließt eine eigene MT-Inversion bewusst aus. | – |
| 20 | InSAR-Pipeline (ISCE, LiCSBAS, MintPy) festlegen. | berechtigter Vorschlag, abgelehnt (Umfang) | Morishita et al. 2020 (10.3390/rs12030424), Lazecký et al. 2020 (10.3390/rs12152430) und Yunjun et al. 2019 (10.1016/j.cageo.2019.104331) sind verifiziert. Das Paper nutzt kein InSAR; InSAR ist für eine spätere Version vorgesehen. | – |
| 21 | Die Methodik sei mit dem „UTAC“-Modell unterfüttert; UTAC, Field Entropy und Phi müssten aus Text und Code entfernt werden. | **halluziniert** (für dieses Paper) | Paper und Code enthalten kein UTAC-Modell, keine „Field Entropy“ und kein Phi-Scaling. „utac“ kommt nur im Repository- und Paketnamen vor. README und `DISCLAIMER.md` sagen ausdrücklich: „no UTAC/CREP/AFET bridge“. Belegt hat Gemini den Vorwurf nur mit anderen Repositories. | Ein Satz in „Data and code availability“: „utac“ ist ein Programmlabel; keine Methode nutzt ein Modell dieses Namens. |
| 22 | Poroelastisches und hydrologisches Forcing wird übersehen. | falsch | Porendruck wird in Einleitung und Discussion genannt (Simon et al. 2025, Talwani et al. 2007); F3 vergleicht Regen und Last; die Limitations nennen die Nichttrennbarkeit in SE-Alaska. | – |
| 23 | Die Early-stage-Tests seien „wertlos“. | falsch | Das Paper formuliert ausdrücklich obere Schranken und MDEs und beansprucht keine Kausalität. | – |

## Nicht übernommene Forderungen (Kurzbegründung)
- **Kein neuer Analyseumfang:** Für PyLith- und 3D-Maxwell-Modelle, die InSAR-Pipeline, die MT-Inversion, ein räumliches FDR- bzw. Empirical-Bayes-Verfahren, Monte-Carlo-MDEs mit vollem ETAS und ein Ogata–Katsura-Mc-Modell wären neue Daten oder Modelle nötig. Wo sinnvoll, sind sie als künftige Arbeit genannt.
- **Keine neue Gezeiten-Hypothese:** Die Umformulierung als Schwellen-Hypothese würde präregistrierte Tests nachträglich ändern; die präregistrierten Inhalte bleiben unverändert.
- **Ad-hominem-Abschnitt:** Die Ausführungen über andere Projekte (Methanhydrate, Korallen) gehören nicht zur Begutachtung dieses Papers.

## Literaturprüfung (Crossref, 2026-10-15)

Alle unten aufgeführten DOIs wurden über Crossref aufgelöst; Titel und Jahr stimmen. Ins Paper neu aufgenommen wurde nur Eibl et al. 2020. Die übrigen Titel dienen der Prüfung oder als Hinweis auf künftige Arbeit.

| Kurzbeleg | DOI |
|---|---|
| Sasgen et al. 2026 | 10.1038/s43247-026-03738-y |
| González et al. 2012 | 10.1038/ngeo1610 |
| van Thienen-Visser & Breunese 2015 | 10.1190/tle34060664.1 |
| Bourne et al. 2014 | 10.1002/2014JB011663 |
| Dieterich 1994 | 10.1029/93JB02581 |
| Kumazawa & Ogata 2013 | 10.1002/2013JB010259 |
| Kumazawa & Ogata 2014 | 10.1214/14-AOAS759 |
| Petrillo & Dal Zilio 2026 | 10.1016/j.epsl.2026.120308 |
| Ogata & Katsura 1993 | 10.1111/j.1365-246X.1993.tb04663.x |
| Amorese 2007 | 10.1785/0120060181 |
| Gardner & Knopoff 1974 | 10.1785/BSSA0640051363 |
| Guastella et al. 2026 | 10.1785/0120250144 |
| Stroup et al. 2007 | 10.1029/2007GL030088 |
| Tanaka et al. 2002 | 10.1029/2001JB001577 |
| Tan et al. 2019 | 10.1016/j.epsl.2019.01.047 |
| Eibl et al. 2020 | 10.1038/s41467-020-15744-5 |
| Pankow et al. 2014 | 10.1130/GSATG191A.1 |
| Dahm et al. 2013 | 10.1007/s10950-012-9295-6 |
| Sokos & Zahradník 2008 | 10.1016/j.cageo.2007.07.005 |
| Zahradník & Sokos 2018 | 10.1007/978-3-319-77359-9_1 |
| Aagaard et al. 2013 | 10.1002/jgrb.50217 |
| Walker et al. 2023 | 10.1093/gji/ggad370 |
| Morishita et al. 2020 | 10.3390/rs12030424 |
| Lazecký et al. 2020 | 10.3390/rs12152430 |
| Yunjun et al. 2019 | 10.1016/j.cageo.2019.104331 |
| Ruppel & Kessler 2017 | 10.1002/2016RG000534 |
| Colledge et al. (Preprint) | 10.1002/essoar.10512456.1 |
| Acosta et al. 2023 | 10.1029/2023GL105455 |
| Astiz et al. 2014 | 10.1785/0220130141 |

**Hinweis:** Crossref führt bei Eibl et al. 2020 „Pàlsson“; korrekt ist Pálsson. Der Eintrag wurde wie geliefert übernommen.
