# Treiber-Register (v0.3)

- **Datei:** `drivers/registry.yaml`
- **Geprüfte DOIs:** `drivers/verified_dois.tsv` (Crossref, 2026-10-11)
- **Validierung:** `glacial_seismic_sensitivity_utac.drivers.check()`, Test `tests/test_v03_drivers.py`

**Felder:** id, name, mechanism, evidence (established | reported | speculative), origin (literature | own_research | ai_report), sources (DOIs), observables, data, status (candidate | active | rejected), introduced_in, prereg (none | exploratory | prospective | frozen:<Ref>), notes.

**Regeln (vom Test erzwungen):**
1. Jeder Eintrag hat mindestens eine DOI, und jede DOI steht in `verified_dois.tsv`.
2. `active` setzt `prereg: frozen:<Ref>` voraus.
3. `rejected` bleibt mit Begründung in `notes` stehen.
4. Einträge mit `origin: ai_report` dürfen nur `candidate` und `speculative` sein.

**Stand:** 17 Einträge. Aktiv ist nur D-GLAC, der P133-Kern (C1/C2). Alle v0.3-Treiber sind `candidate`; die im S2 genutzten (D-MINE, D-SLIDE, D-GAS, D-RES, D-GW, D-CALD, D-GIAPD) tragen `prereg: exploratory`.

Eine neue DOI kommt so ins Register: über die Crossref-API auflösen (z. B. mit `scripts/verify_dois.py` als Vorlage), Titel und Jahr gegen die Zitation prüfen, Zeile in `verified_dois.tsv` ergänzen.

## Motivation für spätere Versionen: Kopplung über Skalengrenzen
Neue Treiber entstehen oft an **Übergängen zwischen Systemen**, nicht innerhalb eines einzelnen Systems. Beispiele aus diesem Register:
- Gletscher → Fels: Eisentlastung und Permafrost bereiten Felsstürze vor (D-GLAC, D-PERMA, D-SLIDE).
- Hang → Talboden: Rutschdämme bilden sich und brechen (D-LDAM).
- Magma → Kruste: Magmaentzug führt zum Calderakollaps (D-CALD).
- Hydrosphäre → Störung: Stauseen und Grundwasser wirken auf Störungen (D-RES, D-GW).
- Atmosphäre/Ozean → Kryosphäre: Wärme greift das Eis an (D-VHEAT).

Ein Register, das Treiber nur nach Einzelsystemen sortiert, übersieht solche Kopplungen leicht. Für künftige Versionen ist deshalb ein Feld `couples: [<ID>, …]` angedacht, das ausgehende Kopplungen erfasst. Dazu kommt eine Prüfung, ob ein Kandidat einen Übergang zwischen zwei bereits erfassten Treibern beschreibt. Das ist **Motivation, kein Befund**. Für jede so gefundene Kopplung gelten dieselben Belegregeln (geprüfte DOI, Status `candidate`, keine Nutzung ohne Präregistrierung).
