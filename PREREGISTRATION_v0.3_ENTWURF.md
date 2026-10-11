# Präregistrierung v0.3 – ENTWURF (nicht eingefroren)

**Status:** ENTWURF zur Prüfung durch J. Römer. Das Einfrieren ist für die Zeit **vor dem 2026-11-01** vorgesehen. Dann bleibt das M8-Fenster frei von Datensichtung, und C1 bleibt unberührt.
- **Maschinenlesbarer Entwurf:** `results/v03/prereg_v03_DRAFT.json`, erzeugt mit `scripts/v03_prereg_draft.py`.
- **Beim Einfrieren:** Die Datei wird als `results/frozen_v03_preregistration.json` geschrieben, ihre SHA-256 hier eingetragen und der Stand committet. Die Zenodo-Archivierung erfolgt mit dem v0.3-Release.

**Abgrenzung:**
- v0.3 ändert nichts an v0.1/v0.2: C1, C2, M1–M7, die Nachträge A1–A7, das Erratum E1 und `lagmodel.RHEOLOGIES` bleiben, wie sie sind.
- Die SHA-256 aller eingefrorenen v0.1/v0.2-Dateien stehen im JSON.

**Ideengeber:** Der Gemini-Deep-Research-Bericht diente nur als Ideenquelle. Faktencheck: `docs/reviews/GEMINI_v0.3_FAKTENCHECK.md`. Alle verwendeten Werte stammen aus Primärquellen mit geprüfter DOI (`drivers/verified_dois.tsv`).

## 1. Kategorien

| Kategorie | Inhalt |
|---|---|
| explorativ | S2-Merkmale und -Kalibrierung, S2b-Rückblickprüfung, Sensitivitätslauf GRACE-Unterschätzung (Sasgen 2026), Groningen-Beschreibung |
| vorab festgelegt, aber datenberührt | Regelreihenfolge und Schwellen des Diskriminators (aus S2: dm_min 0,8; shallow 1 km; n_m45_min 10; dc_max 46 %; min_mts 3; iso_max −0,3) |
| prospektiv | **M8**, Fenster 2026-11-01 bis 2027-10-31 |

## 2. Fallliste und Daten
- Fallliste: S0 (`results/v03/s0_case_list.json`, SHA-256 `19c95091…52302`).
- Snapshots: S1 und S1b (`results/v03/MANIFEST_v03.sha256`).

## 3. M8 – prospektiver Test des Quell-Diskriminators
- **Daten:**
  - **Positive:** alle ComCat-Ereignisse im Fenster mit Typ `landslide`, `mine collapse` oder `collapse`. Für die Klassifikation wird das Label verborgen.
  - **Negative:** alle ComCat-Erdbeben mit M ≥ 5,0 und Tiefe ≤ 40 km im Fenster.
  - **Umfeld:** globaler ComCat-Katalog M ≥ 4,5 für ±0,5 Jahre; für Positive zusätzlich 30 km / ±400 Tage.
  - Der Abruf erfolgt nicht vor dem 2027-11-15.
- **Primärer Endpunkt:** Fehlalarmrate auf den Negativen im Modus `catalogue_only`.
  - Kriterium: Die obere 95-%-Clopper-Pearson-Grenze liegt unter 2 %.
  - Das Kriterium wurde **vor** der S2b-Rückblickprüfung festgelegt (Commit 32e3159).
- **Sekundäre Endpunkte (beschreibend):**
  - Trefferquote je Klasse auf den Positiven (beide Modi, mit KI). Erwartet werden nur etwa 5–8 Positive pro Jahr; die Schätzung ist entsprechend unsicher.
  - Fehlalarmrate im Modus `no_labels`.
  - Sensitivitätsanalyse mit 50 km statt 25 km Ausschluss um die Fallzentren.
- **Berichtspflicht:** Das Ergebnis wird unabhängig vom Ausgang berichtet. Die Schwellen werden nicht nachjustiert.

## 4. Was nicht getestet wird
- Forcing-Kopplung (Groningen, Koyna): Es fehlen Forcing-Zeitreihen über einen freigegebenen offenen Weg. Siehe Entscheidungen.
- GRACE-Unterschätzung: bleibt explorativ; es wird kein Test daraus.
- InSAR und eigene MT-Inversion: nicht in v0.3.

## 5. Offene Entscheidungen vor dem Einfrieren
Siehe `decisions_open` im JSON und `docs/v03/S2_ERGEBNISSE.md`.
