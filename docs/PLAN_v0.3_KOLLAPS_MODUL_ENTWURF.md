# Plan v0.3 – Modul „Massenänderung und Kollaps“ (ENTWURF)

**Status: Entwurf vom 2026-10-11.** Nicht freigegeben. Er wird überarbeitet, sobald die Ergebnisse
der Gemini-Deep-Research-Recherche ([`GEMINI_DEEPRESEARCH_PROMPT_v0.3.md`](GEMINI_DEEPRESEARCH_PROMPT_v0.3.md))
geprüft sind und J. Römer zugestimmt hat. Nichts hiervon ist präregistriert.

## Ziel

Prüfen, ob sich Seismizität, die durch Massenänderung oder Hohlraum-/Reservoirkollaps entsteht,
mit offenen Daten **erkennen und von tektonischer Hintergrundseismizität unterscheiden** lässt –
analog zu Punggye-ri (wiederholte Explosionen, Kollaps 2017, Absenkung, nachlaufende Kleinbeben).
Erst danach wird gefragt, ob es solche Signaturen in Regionen mit Eisverlust gibt. Ergebnisse
werden wie in v0.1/v0.2 mit Obergrenzen berichtet.

## Modulstruktur

1. **Kalibrierfälle** (bekannte Ursache, gute Daten): Kandidaten Punggye-ri 2017,
   Bárðarbunga 2014–15 (Calderakollaps), Groningen (Gasförderung), Koyna–Warna (Stausee),
   Lorca 2011 (Grundwasserentnahme). Weitere aus der Recherche; Auswahl nach Datenlage.
   Kollaps- bzw. Hangereignisse wie Langtang 2015 und die gemeldete Flut im Budhi-Gandaki-Tal
   vom 11.10.2026 (Ursache unbestätigt, mögliche Dammbruch-Hypothese Chumchet) nur, wenn sie
   belastbar dokumentiert sind.
2. **Signatur-Diskriminator:** Merkmale je Ereignisfolge – Momententensor (isotroper/CLVD-Anteil,
   soweit veröffentlicht oder invertierbar), Tiefe, Abklingverhalten (Omori vs. nicht-Omori),
   b-Wert, räumliche Migration, Kopplung an Forcing-Zeitreihen (Förderung, Wasserstand),
   gleichzeitige InSAR/GNSS-Deformation, Coulomb-Spannungsänderung. Erst regelbasiert, ein
   statistisches Modell nur, wenn genug Kalibrierfälle vorliegen.
3. **Regionales Screening:** Anwendung des eingefrorenen Diskriminators auf die P133-Regionen
   (SE-Alaska, Island, Grönland, Alpen, NZ, Patagonien, Himalaya) und auf passende
   Kontrollregionen; Kandidatenliste statt Einzelbefunde.

## Kandidaten-Datenquellen (zu prüfen)

- Kataloge: ComCat, nationale Netze wie in v0.2, ISC; KNMI (Groningen), IMO (Island).
- Momententensoren: GCMT, USGS, nationale MT-Kataloge; Wellenformen über FDSN (EarthScope, GEOFON, ORFEUS).
- Deformation: Sentinel-1 (COMET-LiCSAR/LiCSBAS, ASF), NGL-GNSS.
- Forcing-Zeitreihen: Gasförderung Groningen (NAM/öffentlich), Stausee-Pegel Koyna, Grundwasser Lorca, GRACE/GRACE-FO.
- Literaturwerte (Volumen, Absenkung, Mmax) nur mit geprüfter DOI.

## Meilensteine

1. Recherche-Ergebnis prüfen, Quellen verifizieren, Fallliste festlegen (Freigabe J. Römer).
2. Datenabruf und Archivierung (Snapshots mit SHA-256) für 3–5 Kalibrierfälle.
3. Merkmale berechnen, Diskriminator auf Kalibrierfällen entwickeln (explorativ).
4. Diskriminator, Schwellen und Screening-Regeln einfrieren (Präregistrierung v0.3).
5. Screening der P133-Regionen und Kontrollen; Bericht mit Obergrenzen.
6. Release v0.3.0 mit Zenodo-Archiv; ggf. Ergänzung des Preprints.

## Präregistrierung (was wird vor welchen Daten eingefroren)

- **Explorativ** (nicht präregistriert): alles auf den Kalibrierfällen, deren Daten zwangsläufig
  vorher angesehen werden.
- **Vor dem Screening eingefroren:** Merkmalsdefinitionen, Diskriminator inkl. Schwellen,
  Regionen und Kontrollen, Zeitfenster, Mc-/Declustering-Regeln, Mehrfachtest-Korrektur,
  Power-/MDE-Angaben. Die Screening-Daten der P133-Regionen wurden in v0.1/v0.2 für andere
  Größen angesehen; das Screening ist daher „vorab festgelegt, aber datenberührt“, nicht
  konfirmatorisch – so wird es auch benannt.
- **Prospektiv** (echte Bestätigung): nur Ereignisse nach dem Einfrierdatum, analog zu C1/C2.
- Unveränderlich bleiben alle Dateien von v0.1/v0.2 (C1, C2, Nachtrag A1–A7).

## Was NICHT behauptet wird

- Kein Nachweis, dass Eisverlust Kollapsseismizität auslöst; das Modul prüft zuerst nur, ob
  sich solche Signaturen überhaupt zuverlässig erkennen lassen.
- Keine Gefährdungsprognose für Orte oder Personen; keine Alarmmeldungen.
- Einzelfälle (z. B. Punggye-ri, Flutereignisse) sind Analogien, keine Belege für globale Trends.
- Gemini-Ergebnisse sind nur Ideenquelle; Zahlen und Zitate gelten erst nach eigener Prüfung.
