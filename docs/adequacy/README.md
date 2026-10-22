# `etas_adequacy` – Adäquanzdiagnostik für das eingefrorene v0.2-ETAS-Nullmodell

**Status: explorativ, im Aufbau (Pakete AP0–AP4).** Nichts hier verändert die Präregistrierung, die C2-Statistik, ihre Fenster oder Parameter.

## Zweck

Das Modul prüft *diagnostisch*, ob das eingefrorene zeitliche ETAS-Modell (C2-Nullmodell, `results/frozen_v02_baselines.json`) Daten reproduziert. Es liest die Baselines und importiert `etas_nonstat`, schreibt aber nie in eingefrorene Dateien.

Kernprinzip:
- Ein µ-Anstieg in der **Gletscher**region ist das gesuchte Signal, kein Modellfehler.
- **Niveau-Tests** (N-Test) gelten deshalb nur in der **Kontrollregion** als Adäquanzkriterium.
- **Struktur-Tests** (Residuen in transformierter Zeit, M-Test, N-bedingte Likelihood) gelten in beiden Regionen.

## Pakete

| AP | Inhalt | Stand |
|---|---|---|
| AP0 | Gerüst, nur lesender Baseline-Lader mit SHA-256-Prüfung, Schutztest | ✔ |
| AP1 | Intensität und Kompensator des zeitlichen ETAS, transformierte Zeiten | offen |
| AP2 | Fenstersimulation (Historie nur als Auslöser, auf das Fenster bedingt) | offen |
| AP3 | Teststatistiken: N (Poisson/Mischung), M, Pseudo-LL, Ogata-KS, IG | offen |
| AP4 | Fehlalarmquote und Macht des Gates (Nachtragsvarianten S/L) per Simulation | offen |

Wichtig für AP3/AP4: Wird µ aus denselben Daten neu geschätzt, auf denen der KS-Test läuft, sind die nominellen KS-p-Werte zu groß (Lilliefors-Problem). Die Kalibrierung erfolgt deshalb per **parametrischem Bootstrap**: In jeder Simulation wird µ genauso neu geschätzt wie im echten Verfahren, und nur µ, bei festen eingefrorenen Triggerparametern. AP4 liefert die maßgeblichen Fehlalarmquoten, nicht die Überschlagswerte des Planentwurfs.

## Schutz eingefrorener Dateien (AP0)

`tests/adequacy_frozen_inventory.py` sammelt alle eingefrorenen Hash-Listen aus den Präregistrierungsdokumenten selbst:
- v0.2: `v01_frozen_files_sha256`;
- Nachtrag: `amends_files_sha256_unchanged`;
- v0.3: `sha256_frozen_v01_v02`, `sha256_v03_artefacts`, `sha256_code`;
- dazu die an Tag `v0.2.0` gebundenen Dateien `etas_nonstat.py` und `confirmatory_v02.py`.

Geprüft wird auf zwei Ebenen:
1. je Datei als eigener Test (`tests/test_adequacy_guard.py`);
2. vor und nach **jeder** Testsitzung (`tests/conftest.py`). Ändert sich eine eingefrorene Datei während des Laufs, endet die Sitzung mit Fehler.

Zeilenenden: Eine reine CRLF/LF-Umwandlung (Windows-autocrlf) gilt nicht als Inhaltsänderung. Jede andere Änderung schlägt fehl.

## Grenzen

Rein zeitliches Modell, ohne Raumkern; p liegt in 7 von 8 Regionen an der Grenze 1,0001, mit tmax = 1 a. Ein „bestanden“ heißt bei kleinen Ereigniszahlen oft nur „nicht widerlegbar“. Gate-Schwellen werden **nicht** aus den Daten 2005–2025 abgeleitet.
