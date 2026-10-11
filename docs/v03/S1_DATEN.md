# v0.3 S1 – Daten-Snapshots

- **Abruf:** 2026-10-11, 08:51–09:00 UTC (10:51–11:00 MESZ), mit `python scripts/v03_fetch.py`
- **Ablage:** `data/raw/v03/` (13,5 MB, 718 Dateien). Wie alle Rohdaten ist der Ordner nicht im Git.
- **Im Repo:** `results/v03/MANIFEST_v03.sha256` (sha256sum-kompatibel, Pfade relativ zu `data/raw/v03/`) und `results/v03/s1_snapshots.json` (je Datei Abfrage-URL, Abrufzeit UTC, Bytes, Zeilen, SHA-256).
- **Prüfung:** `scripts/v03_s2_calibration.py` prüft vor jeder Auswertung alle 718 Hashes und bricht bei Abweichung ab.
- **Zeitfenster:** Datenende 2026-10-01 00:00 UTC, also vor dem C1-Fenster ab 2026-11-01. C1 bleibt unberührt.

| Datei | Dienst | Zeilen |
|---|---|---|
| crandall_comcat.csv (30 km, ab 1990) | ComCat | 14 513 |
| bingham_comcat.csv (20 km, ab 1990) | ComCat | 1 051 |
| langtang_comcat.csv (100 km, ab 2000) | ComCat | 350 |
| groningen_knmi.txt (30 km, ab 1986) | KNMI FDSN | 1 842 |
| groningen_comcat.csv | ComCat | 8 |
| lorca_comcat.csv / lorca_emsc.txt | ComCat / EMSC | 227 / 786 |
| punggye_comcat.csv (50 km, ab 2006) | ComCat | 9 |
| bardarbunga_comcat.csv (20 km, ab 1990) | ComCat | 422 |
| koyna_comcat.csv (60 km, ab 1960) | ComCat | 57 |
| budhi_gandaki_comcat.csv (Watchlist) | ComCat | 0 |
| control_* (6 Boxen, M ≥ 2,5, ab 2000) | ComCat | 36–1 564 |
| detail/*.geojson (Schlüsselereignisse, Bárðarbunga M ≥ 5, Kontroll-Hauptbeben M ≥ 4,5) | ComCat | 701 Ereignisse |

**Nicht beschafft:**
- **Groningen-Förderdaten.** Das NLOG-Datacenter ist eine interaktive Web-App. Ein dokumentierter offener Download-Endpunkt wurde nicht gefunden, und eine interne REST-Schnittstelle habe ich bewusst nicht angesprochen. Der TNO-Zenodo-Datensatz (https://doi.org/10.5281/zenodo.21239992) enthält nur GMM- und Fragilitätsdateien.
- **Koyna-Pegeldaten.** Es gibt keine offene Quelle.
- **Wellenformen bzw. eigene MT-Inversion.** Entfällt, siehe Entscheidungen.

**Hinweise zu den Daten:**
- KNMI gibt für Groningen fast durchgängig die feste Tiefe 3,0 km an (1 815 von 1 842 Ereignissen). Die Tiefe ist dort also kein Merkmal.
- ComCat-Momententensoren sind meist deviatorisch (Spur 0). Eine Ausnahme ist der volle MT der UUSS für Crandall.
- `percent-double-couple` liegt in ComCat meist als Bruch vor, bei vier Produkten aber in Prozent. Der Parser behandelt beides.
