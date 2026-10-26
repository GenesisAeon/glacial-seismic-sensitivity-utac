# Zweiter Nachtrag zur Präregistrierung v0.2 – A8 (Adäquanz-Gate) und A9 (C2-Bestätigung ohne Epizentralzone)

**Status: ENTWURF – noch nicht in Kraft.** Wird in Kraft gesetzt und eingefroren am **[Datum]**, **vor** dem Beginn des C2-Fensters (2027-01-01) und vor jedem Datum ab 2027. Maschinenlesbare, verbindliche Fassung: `results/frozen_v04_addendum_[Datum].json`, SHA-256 **[wird beim Einfrieren eingetragen]**. Entscheidung: J. Römer (GenesisAeon). Inhaltliche Entscheidungen: Gate-Variante L + T3 am 2026-10-22 (`docs/adequacy/gate_decision.md`), Simulationszahl und Seed-Regel am 2026-10-22, A9 am 2026-10-23.

Dieser Nachtrag folgt Abschnitt 8 der Präregistrierung v0.2 („jede spätere Änderung ist ein neuer, datierter Nachtrag mit neuem Hash“). **Unverändert** bleiben (SHA-256 in der JSON-Datei, geprüft von `tests/test_v04_addendum.py`): `PREREGISTRATION_v0.2.md`, `results/frozen_v02_preregistration.json`, `results/frozen_v02_baselines.json`, der erste Nachtrag (`results/frozen_v02_addendum_2026-10-10.json`) mit A1–A7, die b-Werte `results/adequacy/b_value/b_value_2016_2025.json` sowie die eingefrorenen Dateien von v0.1.0 und v0.3. Die **C2-Statistik, ihre Blicke und α-Niveaus ändern sich nicht.** A8 und A9 fügen nur hinzu, wann ein C2-Ergebnis als unentschieden gilt (A8) und wann eine Ablehnung als bestätigt gilt (A9). Ausführliche Begründung und Belege: `docs/adequacy/A8_addendum_draft.md` und `docs/adequacy/A9_c2_zone_confirmation_draft.md` (beide mit den Hashes in der JSON festgehalten).

## A8 – Adäquanz-Gate für C2 (Variante L + T3)

**Regel.** C2 gilt als **unentschieden**, wenn in der Kontrollregion **Interior_AK_ctrl** einer der Tests T1, T2 oder T3 **p < 0,005** ergibt. Ein Versagen von T2 oder T3 in der Gletscherregion **SE_Alaska_AK** wird als Einschränkung neben dem C2-Ergebnis berichtet; dieses behält seinen konfirmatorischen Status. Ein Anstieg von µ in der Gletscherregion ist das gesuchte Signal, kein Modellfehler; deshalb kann nur die Kontrollregion C2 unentschieden machen.

**Tests** (alle gegen die eingefrorenen Baselines und b-Werte):
- **T1** Anzahltest der Kontrollregion gegen das eingefrorene Modell (log µ ~ N(log µ_ref, σ_y²), bedingt auf die Vorgeschichte), zweiseitiges Quantil-p, **10.000 Simulationen**.
- **T2** Ogata-KS der transformierten Abstände gegen Exp(1) mit neu geschätztem µ und parametrischem Bootstrap, der µ in jeder Simulation neu schätzt, **B = 10.000**, je Region.
- **T3** Zwei-Stichproben-KS der Fenster-Magnituden gegen die Referenz 2016–2025, je Region, asymptotisches p. Referenz: alle Ereignisse M ≥ 2,1 von 2016-01-01 bis vor 2026-01-01 aus den eingefrorenen Snapshots (5.442 bzw. 2.098 Ereignisse). Fenster und Referenz laufen durch **dieselbe** Verarbeitung (ComCat ak, `catalog.prepare`, Mc ≥ 2,1, Binning 0,1). Vor dem Test werden beide Stichproben auf 6 Nachkommastellen gerundet (Schutz gegen Float-Darstellungen).

**Fenster und Blicke.** Das Gate wird an **jedem** C2-Blick ausgewertet (2029-12-31 und 2036-12-31), jeweils auf dem **ganzen** Fenster [2027-01-01, Ende des Blicks). Die Falsch-Gate-Rate über beide Blicke liegt nach oben abgeschätzt bei höchstens ≈ 0,026.

**Seed und Simulationen.** **Ein** fester ganzzahliger Seed für das ganze Gate: **[Seed – siehe Entscheidungspunkt unten]**. Die Ströme je Test werden mit `np.random.SeedSequence(seed).generate_state(...)` abgeleitet. Es gibt **keinen** zweiten Lauf mit anderem Seed und keine Erhöhung der Simulationszahl, nachdem Daten gesehen wurden. Liegt ein p nahe 0,005, gilt das Ergebnis wie berechnet. Die echte Auswertung läuft mit dem fortsetzbaren Bootstrap (Checkpoints, bitgenau gleich einem ununterbrochenen Lauf).

**Bekannte Grenze.** Die Sequenz des M6,8 vom 2025-12-06 in der Gletscherregion erfasst das Gate nicht; sie kann dort höchstens T2/T3 als Einschränkung auslösen. Den Schutz gegen eine falsche C2-Ablehnung durch diese Sequenz übernimmt A9.

## A9 – C2-Ablehnung zählt nur, wenn sie ohne die Epizentralzone bestehen bleibt

**Regel.** Eine C2-Ablehnung an einem Blick gilt nur dann als **bestätigt**, wenn die **reduzierte Statistik** ein einseitiges p **unter dem α desselben Blicks** hat (0,01 bzw. 0,04). Die reduzierte Statistik ist C2 mit drei Unterschieden:
- Gletscherregion SE_Alaska_AK **ohne** die Kreisscheibe mit Radius **55 km** um das Epizentrum des M6,8 vom 2025-12-06 20:41:51 UTC (60,3503° N, 139,3591° W; ComCat ak); Großkreisabstand, R = 6.371 km; Ereignisse bei genau 55 km zählen als außerhalb;
- **reduzierte Baseline** log µ_ref = **3,99831**, σ_y = **0,38896**;
- Kontrollregion und alles Übrige unverändert.

Eine nicht bestätigte Ablehnung wird berichtet als „C2 lehnt ab, außerhalb der Sequenzzone von 2025 nicht bestätigt“ und zählt nicht als Stütze für H2/C2.

**Herleitung** (vor jedem Datum ab 2027 festgelegt): Radius = 95-%-Quantil der Epizentralabstände der Sequenzereignisse ≥ Mc von Tag 2 bis 2025-12-31 (51,44 km), auf 5 km aufgerundet. Die reduzierte Baseline wird relativ zur eingefrorenen bestimmt (Jahres-log-µ 2016–2025 mit und ohne Zone auf dem eingefrorenen Snapshot). Daten aus 2026 dienten nur zur Beschreibung der Sequenz und zur Kalibrierung der Simulation. Kalibrierung (AP6c): gemeinsame Fehlalarmrate 0,007–0,018, Trennschärfe gegen µ × 1,5 von 0,145/0,695 auf 0,130/0,677.

Maschinenlesbar: `results/adequacy/c2_zone_spec.json` (Status FROZEN, Hash in der Addendum-JSON). Code: `etas_adequacy/zone_check.confirm_c2`.

## Code und Archivierung

Die Auswertung an den Blicken nutzt den Code des Tags **v0.4.0** (A4.6: Reproduktion mit dem veröffentlichten Code). Archivierung auf Zenodo mit dem Release v0.4.0, **vor dem 2027-01-01**. Danach werden A8 und A9 nicht mehr geändert.

---

### Entscheidungspunkt für Johann vor dem Einfrieren: der Gate-Seed
Die Seed-Regel ist beschlossen, der **Wert** fehlt noch. Vorschlag (Claude): Der Seed wird **nicht frei gewählt**, sondern **mechanisch abgeleitet**, z. B. als die ersten 8 Hex-Ziffern des SHA-256 dieses Nachtrags ohne die Seed-Zeile, als Ganzzahl. Er hängt damit an einem Text, der vor 2027 eingefroren wird, und niemand kann ihn nach Ergebnissen „aussuchen“. Alternative: Johann nennt eine Zahl, die in den Nachtrag geschrieben wird. Beides ist mit A8 vereinbar.
