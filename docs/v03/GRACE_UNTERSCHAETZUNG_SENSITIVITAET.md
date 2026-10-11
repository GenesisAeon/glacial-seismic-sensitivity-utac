# v0.3 – Sensitivitätslauf GRACE-Unterschätzung (Sasgen et al. 2026) – EXPLORATIV

**Status:** explorativ und nicht präregistriert. Die eingefrorenen v0.1/v0.2-Ergebnisse bleiben unverändert. Der Lauf ohne Faktor (`none_v02`) reproduziert `results/v02/m4_lag_earliest.csv` exakt (Test `tests/test_v03_grace_bias.py`).

**Quelle:** Sasgen et al. 2026, *Commun. Earth Environ.*, https://doi.org/10.1038/s43247-026-03738-y. Für 2002–2025 ergibt sich mit Niedrigviskositäts-GIA ein zusätzlicher Massenverlust von 7 ± 1 Gt/a in Alaska (rund 9 % mehr) und 3 ± 1 Gt/a in Island (rund ein Drittel mehr).

**Vorgehen** (`src/.../v03_grace_bias.py`, `scripts/v03_grace_bias.py`):
- Die GRACE-basierten Entlastungsraten der Regionen `*_grace` werden skaliert:
  - Alaska: Faktor 1,09 (Spanne 1,077–1,103)
  - Island: Faktor 1,32 (Spanne 1,21–1,43)
- Die Korrektur wird als konstanter Trend behandelt. Die Beschleunigung bleibt deshalb gleich, die relative Beschleunigung ξ sinkt um den Faktor 1/f.
- Gerechnet wird über alle fünf Rheologie-Varianten aus v0.2 M4.
- Die Regionen `*_surface` (Hugonnet-Raten) hängen nicht von GRACE ab und dienen als Referenz.
- **Vereinfachung:** Die relativen Faktoren gelten für Sasgens Regionen. Sie werden hier auf unsere GRACE-Boxen übertragen: SE_Alaska_box mit 17 Mascons, Vatnajökull mit 1 Mascon.

**Ergebnis** (`results/v03/grace_bias_earliest.csv`, früheste Detektion über alle Szenarien):

| Region | L′ heute (kPa/a), v0.2 → zentral | Verschiebung früheste Detektion (Sasgen-Rheologien) | früheste Detektion |
|---|---|---|---|
| SE_Alaska_grace | 1,71 → 1,87 | −1,0 bis −1,5 Jahre | 2059–2064 |
| Iceland_grace | 0,86 → 1,13 | −6,5 bis −15,5 Jahre (v0.1-Rheologie: −34,5 bis −54,5) | ≥ 2095 |
| *_surface | unverändert (7,26 bzw. 8,63) | 0 | 2045–2070 |

**Einordnung:**
1. **Alaska:** Die Korrektur verschiebt die Detektion praktisch nicht.
2. **Island:** Die Detektion rückt deutlich vor, bleibt aber in allen Varianten jenseits von etwa 2095. An der v0.2-Aussage („auf GRACE-Basis keine Detektion in diesem Jahrhundert“) ändert sich nichts.
3. **Wichtiger als die GIA-Korrektur:** Die GRACE-Boxmittel liegen um den Faktor 4–10 unter den Gletscheroberflächen-Raten. Die Wahl der Lastdefinition (Boxmittel oder Gletscherfläche) dominiert die Unsicherheit; die Sasgen-Korrektur schließt nur einen kleinen Teil dieser Lücke.
