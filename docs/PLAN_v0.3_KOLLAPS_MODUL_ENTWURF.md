# Plan v0.3 – Modul „Massenänderung und Kollaps“ (Umsetzungsplan, ENTWURF)

**Status: Entwurf vom 2026-10-11, überarbeitet nach dem Faktencheck des Gemini-Deep-Research-Berichts.**
Nicht freigegeben, nichts hiervon ist präregistriert. Verbindlich wird der Plan erst mit dem OK von J. Römer.

**Grundlagen:**
- Prompt [`GEMINI_DEEPRESEARCH_PROMPT_v0.3.md`](GEMINI_DEEPRESEARCH_PROMPT_v0.3.md);
- Rohbericht [`reviews/raw/gemini_deepresearch_v0.3_mass_change.md`](reviews/raw/gemini_deepresearch_v0.3_mass_change.md), nur als Ideengeber;
- Faktencheck [`reviews/GEMINI_v0.3_FAKTENCHECK.md`](reviews/GEMINI_v0.3_FAKTENCHECK.md).

Übernommen werden nur Angaben, die gegen eine Primärquelle mit DOI geprüft sind.

## 0. Leitplanken

- **Bestehendes bleibt unverändert:** alle Dateien von v0.1/v0.2, also die Präregistrierungen C1 (ab 2026-11-01) und C2 (ab 2027-01-01), der Nachtrag A1–A7, das Erratum E1 und die eingefrorenen Parameter. v0.3 ist ein **zusätzliches** Modul und ändert keine bestehende Analyse.
- **Drei Kategorien:** explorativ / vorab festgelegt, aber datenberührt / prospektiv – wie in v0.2.
- **Nüchterne Sprache:** keine Gefährdungs- oder Alarmaussagen. Befunde werden als Obergrenzen bzw. Effektgrößen mit Unsicherheit berichtet.
- **Ressourcen:** nur offene Daten und die Box (8 CPU, 15 GB RAM, davon ~3 GB frei und geteilt, ~114 GB Platte, keine GPU). ObsPy und Pyrocko sind noch nicht installiert; die Installation in `.venv` ist unkritisch.

## 1. Ziel und Fragestellung

**Hauptfrage:** Lassen sich Ereignisfolgen, die durch Massenänderung oder Kollaps entstehen, mit offenen Daten robust von tektonischer Hintergrundseismizität unterscheiden? Gemeint sind:
- Hohlraumkollaps;
- Reservoir- bzw. Aquifer-Entlastung;
- große Massenbewegungen;
- glaziale bzw. hydrologische Entlastung.

Erst wenn das gelingt, wird in den P133-Regionen nach solchen Signaturen gesucht. Ein Nachweis, dass Eisverlust Kollapsseismizität auslöst, ist **nicht** Ziel von v0.3.

## 2. Übernommene Erkenntnisse aus dem Bericht (geprüft)

### 2.1 Kalibrierfälle (Rangfolge nach Datenlage × Relevanz × Machbarkeit)

| Rang | Fall | Klasse | Geprüfte Quelle | Offene Daten | Machbarkeit Box | Urteil |
|---|---|---|---|---|---|---|
| 1 | Crandall Canyon, 6.8.2007, ML 3,9 | Hohlraumkollaps (Bergbau) | Dreger et al. 2008, https://doi.org/10.1126/science.1157392; Pechmann et al. 2008, https://doi.org/10.1785/gssrl.79.5.620 | UUSS-Katalog; Wellenformen Netz UU und regional via FDSN (EarthScope) | hoch: veröffentlichter MT (implosiv + Nebenkomponente); eigene MT-Inversion optional | aufnehmen (Referenz für ISO/CLVD) |
| 2 | Bingham Canyon, 10.4.2013 | Massenbewegung + kleine Folgebeben | Pankow et al. 2014, https://doi.org/10.1130/GSATG191A.1 | UUSS-Katalog und Wellenformen (FDSN); DEM-Differenzen laut Paper | hoch: ML-/md-Diskrepanz, Ms-Detektion und Folgeaktivität lassen sich aus Katalog und Wellenformen nachrechnen | aufnehmen |
| 3 | Langtang Lirung, 26.8.2026 | Gletscher-/Felskollaps mit Ausbruchsflut | ComCat `us7000tbwb` (Ms_vx 5,2, Tiefe 0, Typ landslide), `us7000tc90` (Ms_vx 4,2); Datenkatalog Liaskos et al. 2026, https://doi.org/10.5281/zenodo.23034746 | ComCat, Copernicus EMSR927, Planet-Open-Data (CC-BY-NC), Sentinel-1/-2 | mittel: Katalog und Wellenformen ja; Prozessstudien laufen noch | aufnehmen als Klasse „Massenbewegungsquelle“ (Kontrast zu Erdbeben) |
| 4 | Groningen, 1991– | Reservoir-Depletion/Kompaktion | van Thienen-Visser & Breunese 2015, https://doi.org/10.1190/tle34060664.1; Bourne et al. 2017, https://doi.org/10.1017/njg.2017.35; TNO-Code https://doi.org/10.5281/zenodo.21239992 | KNMI-Katalog; Förderdaten (öffentlich, Format klären) | hoch für Katalog und Forcing-Kopplung (nichtstationäres ETAS); MT nur aus Literatur | aufnehmen (beste Forcing-Zeitreihe) |
| 5 | Lorca, 11.5.2011, Mw 5,1 | Aquifer-Entlastung | González et al. 2012, https://doi.org/10.1038/ngeo1610 | IGN-Katalog; Grundwasserdaten nur aus der Publikation | mittel: Einzelereignis; ΔCFS-Nachrechnung mit c = 0,5 und B = 0,6 möglich | aufnehmen als Einzelfall-Plausibilitätstest |
| 6 | Punggye-ri, 3.9.2017 (Kollaps nach dem Test) | Hohlraumkollaps nach Explosion | **noch selbst zu recherchieren** (Gemini lieferte nichts) | ComCat/ISC; offene Stationen (z. B. IC.MDJ via FDSN) | offen | erst nach eigener Quellenprüfung |
| 7 | Bárðarbunga 2014–15 | Calderakollaps (natürlich) | **noch selbst zu recherchieren** | IMO-Katalog, GCMT | offen | erst nach eigener Quellenprüfung |
| 8 | Koyna–Warna | Stauseelast | **noch selbst zu recherchieren** | Kataloglage unklar | offen | zurückgestellt |
| 9 | Skaftá-Jökulhlaups 2014/2015 | subglaziale Seeentleerung (Tremor) | Eibl et al. 2020, https://doi.org/10.1038/s41467-020-15744-5 | Array-Daten: Verfügbarkeit unklar | gering für v0.3 | Kandidat für eine spätere Version |
| – | Budhi Gandaki, 11.10.2026 | Erdrutschdamm-Bruchflut (Ursache unbestätigt) | Nachrichten 11.10.2026; **kein** ComCat-Eintrag | – | – | nur Beobachtungsliste; keine Aussage ohne seismischen Befund |
| – | In Salah | Injektion/Thermoelastik | Bericht (nicht im Detail geprüft) | eingeschränkt | gering | nicht für v0.3 |

### 2.2 Diskriminierungsmerkmale (Arbeitsliste, noch nicht eingefroren)

| Merkmal | Grundlage (geprüft) | Bemerkung |
|---|---|---|
| Isotroper/CLVD-Anteil des Momententensors | Dreger 2008; Dahm et al. 2013, https://doi.org/10.1007/s10950-012-9295-6 | Indiz, kein Ausschlusskriterium; ISO bei flachen Quellen schlecht aufgelöst |
| Magnitudendiskrepanz ML vs. md bzw. Ms; langperiodische Energie | Pankow 2014 | typisch für Massenbewegungsquellen |
| Katalogtyp, Tiefe ≈ 0 km und emergente Einsätze | ComCat-Ereignistyp „landslide“ (Langtang 2026) | einfach und offen verfügbar; als Label nutzen, nicht als Wahrheit |
| Zeitverlauf: Omori vs. nichtstationär (μ(t), K(t)) | Kumazawa & Ogata 2014, https://doi.org/10.1214/14-AOAS759 | passt zu unserem zweistufigen ETAS mit μ_y |
| Kopplung an eine Forcing-Zeitreihe | van Thienen-Visser & Breunese 2015; Dahm 2013 | Groningen als Referenz |
| Coulomb-Spannungsänderung aus der Laständerung | González 2012 (c = 0,5, B = 0,6 als Sensitivität) | nur als Plausibilitätstest |
| Mc nach Ogata–Katsura | https://doi.org/10.1111/j.1365-246X.1993.tb04663.x | ergänzend zu MAXC+0,2 |
| Fragenkatalog induziert/natürlich | Dahm 2013 | als Gerüst des regelbasierten Diskriminators |

### 2.3 Modellierungsempfehlungen

1. **Nichtstationäres ETAS:** μ(t) und K(t) mit Glättung und ABIC (Kumazawa & Ogata 2014) als Erweiterung unseres zweistufigen μ_y-Ansatzes. Pflicht ist ein Vergleich gegen das stationäre Modell per AIC/ABIC.
2. **Rate-and-State:** Dieterich 1994 (https://doi.org/10.1029/93JB02581) und Heimisson & Segall 2018 (https://doi.org/10.1029/2018JB015656) bleiben das Antwortmodell.
3. **Momententensoren:** zuerst veröffentlichte MTs verwenden. Eine eigene Inversion (Grond/Pyrocko, GPL-3; https://doi.org/10.5880/GFZ.2.1.2018.003) nur für ≤ 2 Ereignisse, weil die Green's-Function-Stores Platz brauchen.
4. **InSAR:** höchstens LiCSBAS auf fertigen COMET-LiCSAR-Frames (GPL-3), 1–2 Frames. ISCE2/3 ist für die Box zu aufwendig.
5. **Neue Sensitivität für P133:** Sasgen et al. 2026 (https://doi.org/10.1038/s43247-026-03738-y) zeigen, dass GRACE-basierte Eisverluste in Island um ~⅓ und in Alaska um ~9 % zu niedrig sind, wenn die schnelle gegenwärtige GIA fehlt. Für unser Lastmodell (Lag-Modell) heißt das: Der Forcing-Betrag in Island und Alaska könnte unterschätzt sein. Das wird als **zusätzliche Sensitivitätsrechnung** geprüft; v0.2-Parameter bleiben unverändert.

### 2.4 Neue Kandidaten-Treiber (für spätere Versionen, nicht v0.3-Kern)

| ID | Treiber | Belegstatus | Quelle |
|---|---|---|---|
| D-GW | Grundwasserentnahme bzw. Aquifer-Entlastung | berichtet (Einzelfall) | González 2012 |
| D-GAS | Reservoir-Depletion bzw. Kompaktion | etabliert | van Thienen-Visser & Breunese 2015 |
| D-INJ | Injektion inkl. thermoelastischer Abkühlung (CCS) | berichtet; nicht im Detail geprüft | Bericht Ref. 2, 3, 26 |
| D-MINE | Untertage-Hohlraumkollaps | etabliert | Dreger 2008 |
| D-SLIDE | große Massenbewegung als seismische Quelle und mögliche Auslöserin kleiner Beben | Quelle etabliert; Auslösung berichtet (Einzelfall) | Pankow 2014; ComCat Langtang 2026 |
| D-JOK | subglaziale Seeentleerung (Tremor, Kesselabsenkung) | etabliert (Tremor) | Eibl 2020 |
| D-GIAPD | schnelle gegenwärtige GIA in Regionen niedriger Viskosität | berichtet (2026) | Sasgen 2026 |
| D-VHEAT | subglaziale vulkanische Wärme | berichtet; Bezug zur Seismizität **spekulativ** | Loose et al. 2018, https://doi.org/10.1038/s41467-018-04421-3 |
| D-LDAM | Erdrutschdamm-Bruchfluten (Erosion bzw. Entlastung im Tal) | Seismizitätsbezug **spekulativ**, unbelegt | – |
| D-PROGLAC | Füllen bzw. Entleeren proglazialer Seen als Laständerung | **spekulativ** | Wells et al. 2025 nur zur Bathymetrie |
| (noch offen) | Gashydrate, Karst/Erdfälle, Permafrost, Salzkavernen | nicht recherchiert | eigene Recherche nötig |

**Als spekulativ markiert, nicht als Befund verwenden:**
- „Dammbruchfluten induzieren Flankenkollapse und flache Seismizität“;
- „schnelle GIA fördert Dekompressionsschmelzen und vulkanotektonische Seismizität“ (in Sasgen 2026 nicht enthalten);
- „Phasen hoher Gezeitenspannung erhöhen selektiv die Wahrscheinlichkeit großer Beben“.

## 3. Treiber-Register (Idee für v0.3 ff.)

Ein maschinenlesbares Register `drivers/registry.yaml` sammelt alle Treiber, die über die Versionen auftauchen. Das verhindert, dass neue Ideen aus Recherchen unbemerkt in Analysen rutschen. Vorschlag für das Schema:

```yaml
- id: D-SLIDE
  name: Große Massenbewegung als Quelle/Auslöser
  mechanism: Einzelkraft-Quelle; statische Laständerung (Auslösung unbewiesen)
  evidence: established | reported | speculative
  sources: [10.1130/GSATG191A.1]          # nur geprüfte DOIs
  observables: [ML_vs_md, long_period_energy, depth_0, catalog_type]
  data: [ComCat, FDSN-Wellenformen]
  status: candidate | active | rejected
  introduced_in: v0.3-dev
  prereg: none | exploratory | frozen:<Datum/SHA-256> | prospective
  notes: ""
```

**Regeln:**
1. Ein Eintrag braucht mindestens eine geprüfte DOI.
2. Ein Statuswechsel auf `active` setzt eine Präregistrierung voraus.
3. Ein `rejected` bleibt mit Begründung stehen.
4. KI-Berichte dürfen nur `candidate`-Einträge mit `evidence: speculative` vorschlagen.

Im Entwurf bleibt das Register Text. Die Datei wird erst nach Freigabe angelegt.

## 4. Meilensteine (S0–S6) und Einfrierpunkte

Die Schritte heißen S0–S6, weil M1–M7 schon für die Monitoring-Indikatoren vergeben sind.

| Schritt | Inhalt | Ergebnis | Einfrieren / Status |
|---|---|---|---|
| S0 | Freigabe dieses Plans und der Fallliste durch J. Römer; eigene Recherche zu Punggye-ri, Bárðarbunga und Koyna (DOIs prüfen) | Fallliste v0.3 | Fallliste eingefroren (Datum + SHA-256 der Plan-Datei) |
| S1 | Datenabruf für die Kalibrierfälle 1–5 (ComCat/UUSS/KNMI/IGN, Wellenformen ±1 h um Schlüsselereignisse) | `data/raw/v03/…` + `MANIFEST_v03.sha256` | Daten-Snapshot eingefroren (Abrufzeit UTC, Abfrage-URL, SHA-256) |
| S2 | Merkmale je Fall berechnen; regelbasierter Diskriminator; nichtstationäres ETAS für Groningen | Bericht „Kalibrierung“ | **explorativ** |
| S3 | Diskriminator, Schwellen, Regionen und Kontrollen, Zeitfenster, Mc/Declustering, Mehrfachtest-Korrektur, Power/MDE festlegen | `PREREGISTRATION_v0.3.md` + JSON | **eingefroren vor dem Screening** (SHA-256, Git-Tag erst nach OK) |
| S4 | Screening der P133-Regionen und Kontrollen (Kataloge bis zum Einfrierdatum) | Kandidatenliste mit Obergrenzen | „vorab festgelegt, aber datenberührt“ |
| S5 | Prospektive Komponente: nur Ereignisse **nach** dem S3-Datum, Looks analog zu C1/C2 | Monitoring-Indikator (Vorschlag „M8“, Name noch zu klären) | prospektiv; der Name darf nicht mit M6/M7 kollidieren |
| S6 | Release v0.3.0 (Zenodo), ggf. Preprint-Ergänzung | Release | nur nach OK; kein Push, Tag oder Release ohne Freigabe |

**Zeitliche Abgrenzung zu C1:** S3 sollte möglichst vor dem 2026-11-01 liegen oder ausdrücklich nur Daten nutzen, die C1 nicht berühren. C1 wertet ab 2026-11-01 prospektiv aus; v0.3 darf diese Auswertung nicht beeinflussen.

## 5. Machbarkeit

| Baustein | Aufwand Box | Risiko |
|---|---|---|
| Kataloge (ComCat, UUSS, KNMI, IGN) | gering (MB-Bereich) | Formatunterschiede; KNMI-Zugang klären |
| Wellenformen (FDSN) für ≤ 10 Ereignisse | gering bis mittel (≤ 1–2 GB) | Stationsverfügbarkeit |
| ObsPy/Pyrocko installieren | gering | Abhängigkeitskonflikte → separates venv |
| Eigene MT-Inversion (Grond) | mittel (GF-Store mehrere GB, CPU-Stunden) | ISO-Auflösung flacher Quellen begrenzt |
| Nichtstationäres ETAS (Groningen) | mittel (CPU, eigene Implementierung) | Überanpassung → ABIC-Vergleich |
| InSAR (LiCSBAS, 1–2 Frames) | mittel bis hoch (10–30 GB) | optional; nur nach OK |
| ISCE2/3, PyLith-FEM | hoch | nicht vorgesehen |

## 6. Was NICHT behauptet wird

- Kein Nachweis, dass Eisverlust Kollapsseismizität auslöst.
- Keine Gefährdungsprognose für Orte oder Personen; keine Alarmmeldungen.
- Einzelfälle (Lorca, Bingham, Langtang, Budhi Gandaki) sind Analogien, keine Belege für Trends.
- Gemini-Ergebnisse sind nur Ideenquelle. Zahlen und Zitate gelten erst nach eigener Prüfung (siehe Faktencheck).

## 7. Offene Entscheidungen (J. Römer)

1. Freigabe der Fallliste (Rang 1–5 fest, 6–8 nach eigener Recherche).
2. Langtang 2026 als eigene Klasse „Massenbewegungsquelle“ aufnehmen?
3. Eigene MT-Inversion (Grond) oder nur veröffentlichte MTs?
4. InSAR (LiCSBAS) in v0.3 oder später?
5. GIA_PD-Sensitivität (Sasgen 2026) für Island und Alaska als Zusatzrechnung in v0.3?
6. Treiber-Register als YAML-Datei anlegen?
7. Zieldatum für S3 relativ zum Start von C1 (2026-11-01).
