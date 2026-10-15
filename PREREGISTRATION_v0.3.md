# Präregistrierung v0.3 – EINGEFROREN am 2026-10-15

**Status:** eingefroren. Das Einfrieren wurde von J. Römer freigegeben: Stand wie geprüft, Schwellen unverändert. Es geschah vor Beginn des M8-Fensters am 2026-11-01.
- **Maschinenlesbar:** `results/frozen_v03_preregistration.json`, SHA-256 `f9d85cb0dcd151a1aa54fbfa6273fd7ff4c231b97d3453520c272b5260ddba7f`. Erzeugt mit `scripts/v03_freeze_prereg.py`; geprüft durch `tests/test_v03_prereg.py`.
- **Code-Hashes:** Im JSON stehen die SHA-256 von Diskriminator, Merkmalsberechnung und Validierungsskript sowie aller v0.3-Artefakte.
- **Vorgeschichte:** Den Entwurf und seine Entstehung dokumentiert `PREREGISTRATION_v0.3_ENTWURF.md` (abgelöst).
- **Rohdaten:** Die Archivierung auf Zenodo erfolgt mit dem v0.3-Release, Plan siehe `docs/v03/ZENODO_ARCHIV_PLAN.md`.

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

## 5. Bekannte Schwächen (vor dem Einfrieren bekannt und bewusst akzeptiert)
- **(a) Fehlalarm-Risiko durch Regel R2:**
  - Im Rückblick (S2b) ergab der passende Negativ-Satz M 2–4,5 5 Fehlalarme bei 900 Ereignissen. Die obere 95-%-Clopper-Pearson-Grenze liegt bei 1,29 %, das Kriterium bei 2 %.
  - Alle 5 Fehlalarme entstehen über R2: flaches Ereignis innerhalb einer Stunde nach einem größeren. 3 davon liegen im St.-Elias-Gebiet (ak), je 1 in The Geysers (nc) und in South Carolina (se).
  - **M8 kann daher realistisch scheitern.**
- **(b) R4 ist nicht übertragbar:**
  - R4 verlangt einen Cluster-Median-DC ≤ 46 % und ist damit faktisch auf Bárðarbunga 2014 zugeschnitten.
  - Kīlauea 2018 wird mit 0/64 nicht als Calderakollaps erkannt; der Median-DC liegt bei 70,5 % (n = 62).
- **(c) Napoleonville 2012 wird bauartbedingt nicht erkannt:**
  - Der publizierte Momenttensor zeigt eine Volumenzunahme und gehört deshalb nicht zur Kollaps-Klasse.
  - Im ComCat-Katalog fehlt das Ereignis.
- **Folge:**
  - Verbesserungen der Regeln kommen erst in **v0.4**. Sie berühren M8 nicht.
  - M8 läuft mit den eingefrorenen Regeln und Schwellen. Das Ergebnis wird unabhängig vom Ausgang berichtet.
