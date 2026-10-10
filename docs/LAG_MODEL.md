# Lag- und Detektionsmodell (F5)

*Code:* `src/glacial_seismic_sensitivity_utac/lagmodel.py`. *Ergebnisse:* `results/lag_*.csv`.
*Charts:* `charts/08_*`, `09_*`, `10_*`.

**Kein Vorhersagemodell.** Es ist ein Szenariorechner, der eine Frage beantwortet: *Wann könnte eine
verzögerte (viskose) seismische Antwort auf die heutigen Schmelzraten mit der heutigen Katalogleistung
überhaupt nachweisbar werden?* Siehe `honesty.is_lag_model_a_forecast()` → `False`.

## Bausteine

1. **Mantelrelaxation.** Viskoser Halbraum unter einer elastischen Platte bei einer Lastwellenlänge λ:
   - τ = 4πη / (ρ_m g λ) · 1/(1 + D k⁴/(ρ_m g)), mit k = 2π/λ und D = E h³ / (12(1−ν²)).
   - Der Gleichgewichtsanteil der isostatischen Antwort ist C = 1/(1 + D k⁴/(ρ_m g)).
   - Quelle: Turcotte & Schubert (2002), *Geodynamics*, Abschn. 6-10; Herleitung bei Sandwell,
     http://topex.ucsd.edu/geodynamics/glacial_rebound.pdf.
   - Kontrollwert aus dieser Quelle: Fennoscandia, λ = 3000 km, τ = 4400 Jahre → η = 1,1·10²¹ Pa s.
     Unser Code liefert ~4500 Jahre (Test `test_relaxation_time_reference_values`).
2. **Spannung.** Der viskose Anteil der Coulomb-Spannungsrate wird so angesetzt:
   - Ṡ_GIA(t) = κ · C · L̇ · (1 − e^{−(t−t0)/τ}), bei konstanter Entlastung L̇ seit t0 = 1995.
   - **κ** (Oberflächenlast → Coulomb-Spannung auf seismogenen Verwerfungen) ist **nicht** durch Daten
     bestimmt. Wir variieren κ = 0,1 / 0,3 / 1. κ = 1 ist eine bewusst obere Schranke.
3. **Seismizität.** Rate-and-State nach Dieterich (1994):
   - Für langsame Änderungen gilt R/r = (Ṡ0 + Ṡ_GIA)/Ṡ0.
   - Hintergrund Ṡ0 = 10 oder 30 kPa/Jahr. 30 kPa/Jahr ist der kalifornische Wert bei Sirorattanakul & Avouac 2026.
   - t_a = aσ/Ṡ0 ist dort 0,05–1 Jahr. Die Verzögerung kommt also vom Mantel, nicht von der Reibung.
4. **Detektion.**
   - Ein Poisson-Log-Trend über ein Beobachtungsfenster ab 2026-11 ist nachweisbar, wenn seine Steigung ≥ 2,487 · SE beträgt (α = 5 % einseitig, Power 80 %).
   - Dabei gilt SE ≈ √(φ / Σ nᵢ(tᵢ − t̄)²).
   - N/Jahr und φ stammen aus dem echten declusterten Katalog der jeweiligen Region.

## Eingaben mit Quellen

- **Viskositäten:**

  | Region | η [Pa s] | Te [km] | Quelle |
  |---|---|---|---|
  | Patagonien (SPI) | 1,6·10¹⁸ (alternativ 8·10¹⁸) | 36,5 | Lange et al. 2014, doi:10.1002/2013GL058419 |
  | Amundsen-See | 4·10¹⁸ | ~55 | Barletta et al. 2018, doi:10.1126/science.aao1447 |
  | Island/Vatnajökull | 4–10·10¹⁸ (bevorzugt 8–10) | 10–20 | Pagli et al. 2007, doi:10.1029/2006JB004421 |
  | SE-Grönland | ~1·10¹⁹ | (60, *angenommen*) | Khan et al. 2016, doi:10.1126/sciadv.1600931 |
  | SE-Alaska | 1,4·10¹⁹ – 3,7·10¹⁹ | 60 | Larsen et al. 2004/2005, doi:10.1111/j.1365-246X.2004.02356.x, 10.1016/j.epsl.2005.06.032 |
  | Alpen | 1,4–2,8·10²⁰ (2,2 bei 50 km EET) | 50 | Mey et al. 2016, doi:10.1038/ncomms13382 |
  | Fennoskandia (Referenz) | 1,1·10²¹ | – | Turcotte & Schubert / Sandwell |

  Einige Werte stammen aus Abstracts bzw. Such-Auszügen, nicht aus dem Volltext. Sie sind in `constants.py` als `via_abstract_or_snippet` markiert.
- **Lastwellenlängen λ** (≈ 2 × Breite der schwindenden Eismasse) sind **unsere Annahmen** und werden variiert. Sie stehen in `RHEOLOGIES`.
- **Entlastungsraten L̇:**
  - „grace_box_mean“: GRACE-Trend 2002–2026 über die ganze Analysebox. Er ist verschmiert und deshalb klein, z. B. SE-Alaska 1,7 kPa/Jahr.
  - „glacier_surface“: spezifische Massenänderung 2000–2019 nach Hugonnet et al. 2021 (doi:10.1038/s41586-021-03436-z). Island −0,88 m w.e./Jahr ≈ 8,6 kPa/Jahr, Südanden −0,67, südlicher arktischer Gürtel inkl. Alaska −0,74. Für die Alpen ist im Text nur das außerpolare Mittel −0,69 angegeben.

## Ergebnisse

**Relaxationszeiten** (zentrale λ; Tabelle `results/lag_relaxation_times.csv`):

| Region | τ | C |
|---|---|---|
| Patagonien | ~23 Jahre (1,6·10¹⁸) bzw. ~117 Jahre (8·10¹⁸) | 0,36 |
| Amundsen | ~55 Jahre (λ = 500 km) | – |
| Island | ~150–380 Jahre | 0,61 |
| SE-Grönland | ~115 Jahre | 0,94 |
| SE-Alaska | ~64–170 Jahre | 0,11 |
| Alpen | ~1000–2000 Jahre | 0,18 |
| Fennoskandia | ~4500 Jahre | – |

Die Spanne reicht also von Jahrzehnten (Patagonien, Amundsen) bis Jahrtausenden (Alpen).

**Wichtige, nicht offensichtliche Folge:**
- Bei **schmalen Gebirgslasten auf dicker Lithosphäre** ist C klein: SE-Alaska λ = 300 km → C ≈ 0,11; Alpen ≈ 0,18. Der Großteil der Antwort ist dort **elastisch und sofort**. Der verzögerte viskose Anteil ist klein, und in den Alpen zusätzlich extrem langsam.
- Das Frühstadium-Argument („flacher Trend = keine Entwarnung“) trifft am stärksten auf **breite Lasten über weichem Mantel** zu: SE-Grönland (C ≈ 0,94), Island, Amundsen.
- Bei Gebirgsgletschern ist ein heute flacher Trend vergleichsweise *informativer*.

**Szenarien** (`results/lag_detection_scenarios.csv`, 126 Kombinationen):

- Selbst im oberen Extremszenario (κ = 1, Ṡ0 = 10 kPa/Jahr, Gletscheroberflächen-Last) liegt der *viskos verzögerte* Ratenzuwachs 2036 bei ≤ +19 % (Patagonien) und 2100 bei ≤ +27 % (Island).
- Mit der verschmierten GRACE-Boxlast liegt er bis 2100 überall bei ≤ +5 %.
- Ein **Trend** ab 2026 wird in **118 von 126** Szenarien innerhalb von 500 Jahren **nicht** nachweisbar. Die 8 Ausnahmen (Island Gletscheroberfläche, SE-Alaska η = 3,7·10¹⁹, κ ≥ 0,3) erreichen die Nachweisgrenze frühestens **~2155**.
- **Folgerung:** Über Ratentrends ist eine verzögerte GIA-Antwort mit heutiger Katalogleistung praktisch unbeobachtbar. Ein flacher Trend schließt sie deshalb nicht aus (`honesty.does_flat_trend_exclude_delayed_response()` → `False`), kann sie aber auch nicht belegen.
- Messbar sind nur die **sofortigen** Kanäle: elastische Saisonlast und Porendruck. Genau darauf zielen F1/F2.

**Rate-and-State-Saisonmodulation** (`results/lag_rsm_seasonal_modulation.csv`, Chart 10):

- Bei T ≫ t_a ist die Modulation ≈ 2πΔS/(T·Ṡ) und **sinkt**, wenn GIA zusätzliche Spannungsrate liefert. Beispiel: ΔS = 1 kPa, aσ = 1,5 kPa, Ṡ0 = 10 → Modulation 0,43 ohne und 0,38 mit +3 kPa/Jahr.
- Wachsende Empfindlichkeit ist daher **nicht** die generische RSM-Erwartung (`honesty.is_growing_sensitivity_the_generic_rate_state_expectation()` → `False`).
- Fände man sie, wäre das ein Hinweis auf andere Prozesse:
  - sinkende effektive Normalspannung (Schmelzwasser-Porendruck, Mont Blanc: Simon et al. 2025);
  - Annäherung an das Versagen (Parkfield: Sirorattanakul & Avouac 2026; Gezeitentriggerung vor Sumatra/Tohoku nach Tanaka, dort zitiert).
- Abnehmende Modulation (Island, siehe RESULTS) ist dagegen mit steigender Hintergrund-Spannungsrate vereinbar, z. B. nach der Bárðarbunga-Episode 2014–15. Das ist eine **Hypothese, kein Befund**.

## Grenzen des Modells

- **Struktur:**
  - Halbraum + Platte, eine Wellenlänge, keine Asthenosphären-Schicht (Alaska: ~110 km dünner Kanal, Larsen et al. 2005), keine 3-D-Viskosität.
  - Ein Kanal macht kurze Wellenlängen *schneller* als der Halbraum. Die τ-Werte sind deshalb Größenordnungen.
- **Parameter:** κ ist unbestimmt, und die LIA-Vorgeschichte fehlt. In SE-Alaska begann die Entlastung ~1770 (Larsen et al. 2005); ein Teil der viskosen Antwort läuft also seit langem. Wir modellieren nur die Beschleunigung seit ~1995.
- **Was das Modell nicht beschreibt:**
  - Einzelne große Brüche nahe dem Versagen (Pärvie-artig; „clock advance“) beschreibt das Modell **nicht**. Es behandelt Raten, keine Einzelereignisse.
  - Vulkanische Effekte (Dekompressionsschmelzen) sind nicht enthalten.

## Kontext: laterale Heterogenität des Mantels (nur Einordnung)

- Choi, Kim, Kang et al. (2026), „Complex Upper-Mantle Anisotropy Beneath the Pacific Triangle Revealed by Shear-Wave Splitting“, *Seismological Research Letters*, https://doi.org/10.1785/0220260089. Datengrundlage sind 128 Scherwellen-Splitting-Messungen des Oldest-1-Ozeanboden-Arrays über der ältesten Pazifischen Platte.
- Befund: Die schnellen Richtungen variieren regional stark. Sie lassen sich weder allein durch die heutige Plattenbewegung noch durch die alten Spreizungsrichtungen erklären. Um einen hochgeschwindigen, mechanisch festen Lithosphärenblock herum drehen sie systematisch. Die Autoren deuten das als Kopplung der Manteldeformation an diesen Block.
- Bezug hier: ein Beleg aus einem ganz anderen tektonischen Umfeld, dass Mantelstruktur und -deformation lateral stark variieren. Das stützt den Ansatz, Viskositäten regionsspezifisch (Sasgen et al. 2026) statt global einheitlich anzusetzen. Für die glazialen Regionen liefert die Arbeit **keine** Viskositätswerte.
- Hinweis zur Zitierung: Erstautor laut Crossref ist S.-H. Choi, nicht „Kim“.
