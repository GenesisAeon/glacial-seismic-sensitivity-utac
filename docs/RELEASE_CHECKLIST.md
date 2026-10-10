# Release-Checkliste

Stand 2026-10-10 (v0.1.0):

- **Erledigt:**
  - P133 ist als KLIMA-KRYO-13 in `PACKAGE_REGISTRY.md` eingetragen.
  - Zenodo-GitHub-Integration ist eingeschaltet (Johann).
  - `PYPI_API_TOKEN` liegt im Environment `pypi`.
  - Tag `v0.1.0` → `.github/workflows/release.yml` baut, testet, lädt auf PyPI hoch und erstellt das
    GitHub-Release. Zenodo archiviert das Release.
- **Danach:**
  - DOI in `CITATION.cff` und in die READMEs eintragen (Folgecommit, kein neuer Tag).
  - Auf Trusted Publishing umstellen (Johann).

## 1. Vor dem ersten Release entscheiden

- [x] **Paketnummer:** P133 / KLIMA-KRYO-13 eingetragen (2026-10-10). Ursprünglicher Punkt: P133 war provisorisch. Prüfen, ob 133 im `PACKAGE_REGISTRY.md` noch frei ist,
      dann dort eintragen (Domain Klima/Glaziologie/Seismologie, Begleitpaket zu P101). Bei anderer
      Nummer anpassen: `constants.PACKAGE_ID`, `CITATION.cff`, `.zenodo.json`, beide READMEs,
      `PREREGISTRATION.md`-Titel.
- [ ] **Version:** 0.1.0 (Analyse- und Präregistrierungsstand) oder 1.0.0. Empfehlung: 0.1.0, weil
      der konfirmatorische Teil erst 2029/2036 ausgewertet wird.
- [ ] **Präregistrierung zeitlich belegen:** Ein Zenodo-DOI *vor* dem 2026-11-01 würde den
      Einfrierzeitpunkt unabhängig dokumentieren. Der Git-Commit allein ist schwächer, weil
      Commit-Daten änderbar sind. Alternativ: OSF-Präregistrierung mit Link auf den Commit.

## 2. Zenodo

- [ ] Auf https://zenodo.org/account/settings/github/ das Repository
      `GenesisAeon/glacial-seismic-sensitivity-utac` einschalten (Schalter pro Repo, nicht aus einem
      Workflow setzbar).
- [ ] `.zenodo.json` prüfen: Community `genesisaeon`, Ersteller, Affiliation, `related_identifiers`
      (P101 als `isSupplementTo`).
- [ ] Nach dem Release DOI in `CITATION.cff` und README eintragen (Folgecommit, kein neuer Tag nötig).

## 3. PyPI (optional)

- [ ] Paketname `glacial-seismic-sensitivity-utac` auf PyPI prüfen.
- [ ] Secret `PYPI_API_TOKEN` im GitHub-Environment `pypi` anlegen (oder Trusted Publishing einrichten).
- [ ] Für Pre-Releases (`-rc`, `-alpha`, `-beta`): Secret `TEST_PYPI_API_TOKEN` im Environment `testpypi`.
- [ ] Hinweis: Das sdist schließt `data/`, `logs/`, `results/series/` aus. Rohdaten werden nie
      veröffentlicht, sie werden mit `glacial-sensitivity fetch` neu geladen.

## 4. Release auslösen

```bash
git tag -a v0.1.0 -m "v0.1.0: retrospective tests + frozen pre-registration"
git push origin v0.1.0
```

Das startet Build, Tests, PyPI-Upload (falls Token vorhanden) und GitHub-Release; Zenodo archiviert,
falls eingeschaltet.

## 5. Termine für den konfirmatorischen Test

- 2029-11-30: Daten bis 2029-10-31 abrufen (`GSS_END=2029-12-01 glacial-sensitivity fetch --force`),
  `python -m glacial_seismic_sensitivity_utac.confirmatory 2029-10-31`, Ergebnis unverändert berichten.
- 2036-11-30: dasselbe mit `2036-10-31`.
- Abweichungen vom Protokoll nur im `CHANGELOG.md` unter „Pre-registration amendments“.
