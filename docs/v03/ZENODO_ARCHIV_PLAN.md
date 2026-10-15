# Zenodo-Archiv der v0.3-Rohdaten – Plan (vorbereitet, NICHT hochgeladen)

**Inhalt und Größe:**
- 6 158 Rohdateien aus S1, S1b und S1c, unkomprimiert etwa 342 MB.
- Als Paket `gss-utac-v03-raw-snapshots.tar.gz` sind es 75,9 MB.

**Paket bauen:**
- Befehl: `python scripts/v03_zenodo_package.py`
- Das Paket landet außerhalb des Repos in `../zenodo_v03_package/`.
- Das Skript prüft vorher jede Datei gegen `results/v03/MANIFEST_v03.sha256`.
- Das tar.gz ist deterministisch: Reihenfolge sortiert, mtime 0.
- Beim Probelauf am 2026-10-15 lag die SHA-256 des tar.gz bei `d7605605…3fbc4e`. Diese Summe dient nur der Kontrolle; maßgeblich sind die Datei-SHA-256 im Manifest.

## Dateien im Zenodo-Datensatz
- **`gss-utac-v03-raw-snapshots.tar.gz` und `.sha256`:** das Datenpaket mit Prüfsumme.
- **`MANIFEST_v03.sha256`:** SHA-256 jeder Datei.
- **`s1_snapshots.json`:** Herkunft je Datei, also URL, Abrufzeit (UTC) und SHA-256. Bei aufgeteilten Abrufen sind die URLs mit „ | “ verbunden.
- **`frozen_v03_preregistration.json`:** zeigt, dass die Daten vor M8 eingefroren wurden.

## Metadaten (Vorschlag)
- **Titel:** „glacial-seismic-sensitivity-utac v0.3 – raw catalogue snapshots (S1/S1b/S1c)“
- **Typ:** Dataset
- **Creator:** J. Römer (GenesisAeon)
- **Version:** 0.3.0
- **Related identifiers:**
  - `isSupplementTo` → GitHub-Release v0.3.0 und die Software-DOI, sobald sie vergeben ist.
  - `isDerivedFrom` → die Quell-Dienste.
- **Beschreibung:**
  - Momentaufnahmen der Kataloge per FDSN-Abfrage, jeweils mit Abrufzeit.
  - Ein späterer erneuter Abruf kann wegen Katalog-Revisionen abweichen; deshalb wird archiviert.

## Quellen und Lizenzen (vor dem Hochladen klären)
| Quelle | Dateien | Status |
|---|---|---|
| USGS ComCat (`earthquake.usgs.gov`) | alle bis auf zwei | US-Bundesdaten, gemeinfrei; Quellenangabe |
| KNMI RDSA FDSN (`rdsa.knmi.nl`) | `groningen_knmi.txt` | Lizenz vor dem Hochladen prüfen (KNMI-Daten offen, Bedingungen bestätigen) |
| EMSC (`seismicportal.eu`) | `lorca_emsc.txt` | Weiterverbreitung prüfen; falls unklar, aus dem Paket nehmen und nur URL + SHA-256 angeben |

Vorgeschlagene Lizenz für den Datensatz: CC BY 4.0. Dateien, die anderen Bedingungen unterliegen, werden in der Beschreibung ausgewiesen.

## Ablauf (jeder Schritt erst nach Freigabe durch J. Römer)
1. Lizenzfragen KNMI und EMSC klären.
2. Paket neu bauen und die Summen gegen das Manifest prüfen.
3. Zenodo-Entwurf manuell anlegen, Dateien und Metadaten eintragen, dann veröffentlichen. Damit ist die DOI vergeben.
4. Die DOI in README, `docs/v03/S1_DATEN.md` und in der CITATION eintragen und committen.
5. Das GitHub-Release v0.3.0 erstellen. Die vorhandene Zenodo-GitHub-Integration erzeugt die Software-DOI.
