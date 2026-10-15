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
- Fallliste: S0 (`results/v03/s0_case_list.json`, SHA-256 `19c95091…52302`) und Nachtrag A1 mit Napoleonville 2012 und Kīlauea 2018 (`results/v03/s0_amendment_A1.json`, SHA-256 `c066c92d…fcdc`).
- Snapshots: S1, S1b, S1c (`results/v03/MANIFEST_v03.sha256`, 6 158 Dateien, geprüft). Die Rohdaten liegen außerhalb von git; sie werden mit dem v0.3-Release auf Zenodo archiviert.

## 3. M8 – prospektiver Test des Quell-Diskriminators
- **Primärfenster:** 2026-11-01 bis 2027-10-31. Der Abruf erfolgt nicht vor dem 2027-11-15.
- **Zweites Jahr:** 2027-11-01 bis 2028-10-31, nur beschreibend und ohne Kriterium. Abruf ab 2028-11-15.
- **Positive:** alle ComCat-Ereignisse im Fenster mit Typ `landslide`, `mine collapse` oder `collapse`. Für die Klassifikation wird das Label verborgen.
- **Negative, zwei Sätze:**
  - `global_M5`: alle ComCat-Erdbeben mit M ≥ 5,0 und Tiefe ≤ 40 km.
  - `matched_M2_4.5`: ComCat-Erdbeben mit 2,0 ≤ M ≤ 4,5 aus den Netzen, die Positive beigetragen haben. Je Netz werden höchstens 150 Ereignisse zufällig gezogen (Seed 20271115, ohne Zurücklegen).
- **Primärer Endpunkt:** Fehlalarmrate im Modus `catalogue_only`.
  - Kriterium: Die obere 95-%-Clopper-Pearson-Grenze liegt für **beide** Sätze jeweils unter 2 %; beide Bedingungen müssen gelten.
  - Das Kriterium für `global_M5` wurde vor S2b festgelegt (32e3159), das für den passenden Satz vor dessen Rückblickergebnis (d01657a vor 6cb1537).
- **Sekundär (nur beschreibend):**
  - Trefferquote je Klasse mit KI, sowohl für alle Positiven als auch für die Teilmenge M 2–4,5.
  - Fehlalarmraten im Modus `no_labels`.
  - Sensitivitätsanalyse mit 50 km statt 25 km Ausschluss.
- **Rückblick (explorativ, Schwellen unverändert):**
  - Fehlalarme: 0/1 594 (obere Grenze 0,23 %) und 5/900 (obere Grenze 1,29 %).
  - Trefferquoten: Kollaps 2/21, Rutschung 1/55.
  - Kīlauea wird mit 0/64 nicht erkannt (Median-DC 70,5 %), siehe `docs/v03/S2_ERGEBNISSE.md`.
- **Berichtspflicht:** Das Ergebnis wird unabhängig vom Ausgang berichtet. Die Schwellen werden nicht nachjustiert.

## 4. Was nicht getestet wird
- Forcing-Kopplung: Groningen wird ohne Forcing-Test geführt; ein späterer manueller NLOG-Export durch J. Römer ist optional. Koyna dient nur als Negativfall auf Katalogbasis.
- Eigene MT-Inversion, InSAR: nicht in v0.3.
- GRACE-Unterschätzung: bleibt explorativ.
- Die skalenübergreifende Kopplung ist nur als Hinweis beschrieben (`docs/v03/TREIBER_REGISTER.md`), nicht als Test.

## 5. Offene Punkte vor dem Einfrieren
- Abschließende Prüfung durch J. Römer und Festlegung des Einfrierdatums (vor dem 2026-11-01).
