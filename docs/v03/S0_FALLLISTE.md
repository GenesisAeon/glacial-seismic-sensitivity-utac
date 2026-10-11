# v0.3 S0 – Eingefrorene Fallliste

- **Eingefroren:** 2026-10-11 (UTC-Zeitstempel in der Datei), Branch `v0.3-dev`
- **Datei:** `results/v03/s0_case_list.json`
- **SHA-256:** `19c950912a7f407da46e0ee8b6ac45f32e405c32b79f131e3e4d16118de52302`
- **Erzeugt durch:** `python scripts/v03_freeze_s0.py`. Das Skript verweigert das Überschreiben einer abweichenden Datei. Eine Änderung braucht einen datierten, begründeten Nachtrag.
- **Quelle der Inhalte:** `src/glacial_seismic_sensitivity_utac/v03_cases.py`.

| Rang | Fall | erwartete Quellklasse | Forcing-Kontext | Status | Schlüsselereignis |
|---|---|---|---|---|---|
| 1 | Crandall Canyon 2007 | collapse | Kohlebergbau | Kern | ComCat uu50342430 |
| 2 | Bingham Canyon 2013 | mass_movement | Tagebau | Kern | nur publiziert (nicht in ComCat) |
| 3 | Langtang 2026 | mass_movement (eigene Klasse „Massenbewegungsquelle“) | – | Kern | us7000tbwb, us7000tc90 |
| 4 | Groningen | tectonic | Gasförderung | Kern | größtes KNMI-Ereignis (Regel) |
| 5 | Lorca 2011 | tectonic | Grundwasserentnahme | Kern | usp000j1en |
| 6 | Punggye-ri 2017 | collapse | Kernexplosion 8,5 min vorher | Kern | us2000aetk |
| 7 | Bárðarbunga 2014–15 | caldera_collapse | Magmaentzug | Kern | alle M ≥ 5 im Radius 15 km (Regel) |
| 8 | Koyna | tectonic | Stausee | Kern, eingeschränkt | iscgem828259 |
| – | Budhi Gandaki 2026 | (mass_movement) | unbestätigt | nur Watchlist | keines |

**Kontrollen (erwartete Klasse `tectonic`):** alle ComCat-Erdbeben mit M ≥ 4,5 seit 2000 in sechs Boxen: Utah/Intermountain, Nepal-Himalaya, Island, SE-Spanien, Korea/NO-China und W-Indien. Ausgenommen sind Ereignisse im Umkreis von 25 km um die Fallzentren. Magna 2020 (uu60363602) ist zusätzlich benannt.

**Nicht in S0:** Skaftá (Plan-Rang 9; Tremor statt Katalogseismizität). Napoleonville 2012 und Kīlauea 2018 sind als optionale Zusatzfälle vorgeschlagen (Entscheidung offen).

**Wichtig zur Klassenlogik:** Die Quellklasse beschreibt den physikalischen Herd. Lorca, Koyna und Groningen haben eine tektonische Scherquelle mit anthropogenem bzw. hydrologischem Forcing. Für den Quell-Diskriminator sind sie deshalb Negativfälle; ihr Forcing liegt auf einer eigenen Achse.
