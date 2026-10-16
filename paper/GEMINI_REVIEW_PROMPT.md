# Gemini review prompt for the P133 preprint (draft v0.2.1)

Paste the text below into Gemini together with `P133_preprint.pdf`.

---

You are acting as a critical, independent peer reviewer for a seismology / geophysics journal. Attached is the preprint draft "Is seismicity in glaciated regions becoming more sensitive to unloading? Early-stage tests, upper bounds and a preregistered confirmatory design" (J. B. Römer, independent researcher). It reports retrospective tests (1990-2025) of seasonal modulation, load sensitivity, criticality indicators, a two-stage time-varying-background ETAS model, tidal-phase tests, a viscoelastic lag model, tipping and "deceptive quiet" scenarios, GRACE/GNSS monitoring indicators, an exploratory global baseline, and two preregistered prospective tests (C1, C2). Code and data: https://github.com/GenesisAeon/glacial-seismic-sensitivity-utac (Zenodo DOIs 10.5281/zenodo.23281091 and 10.5281/zenodo.23286492).

Please write a rigorous, skeptical review. Do not be polite at the expense of substance; I want problems found now, not after submission. Cover at least:

1. Methodology
   - Catalogue handling: completeness (MAXC + 0.2, 90 % quantile of yearly Mc), nearest-neighbour declustering (Zaliapin & Ben-Zion) and the Gardner-Knopoff alternative; network changes and magnitude-type changes as confounders.
   - Choice of regions, boxes, controls and periods; whether the in-network controls are adequate.
   - The viscoelastic lag model (thin plate over half-space), the rate-and-state (Dieterich) seismicity model, the tipping and stress-shadow ("deceptive quiet") scenarios: are the assumptions stated, are the results presented as scenarios rather than forecasts, and are any physically implausible?
2. Statistics
   - ETAS: two-stage fit with yearly background, Omori kernel truncated at 1 yr, Omori p at its lower bound in 7 of 8 regions, conditional covariance, the standard-error inflation factor 1.25 and its null calibration (Erratum E1). Is the H2.1 difference-in-differences test valid, and is the paper's interpretation of it (formally positive but not robust) correct?
   - b-value estimation and the tidal b-value split; Schuster tests; the random-time null used for ocean-loaded tidal phases.
   - Calibration and power: MDE calculations, power statements for C1/C2, permutation and IAAFT surrogate tests.
   - Multiple testing: Benjamini-Hochberg families, whether the families are defined sensibly, and whether any reported result escapes correction.
3. Claims versus results: check that every claim in the abstract, discussion and conclusions is supported by the numbers in the results sections and tables. Flag any number that is inconsistent between sections, tables and figures.
4. Preregistration honesty: is the distinction between pre-specified but data-touched retrospective tests, exploratory analyses and truly prospective tests (C1, C2) clear and correct everywhere? Are the integrity statements (hashes, commit order, addendum A1-A7) appropriate, and is anything implied to be more confirmatory than it is?
5. Missing or misused literature: important work on glacial/hydrological loading and seismicity, GIA and fault stability, ETAS with time-varying background, seasonal and tidal triggering, or seismic quiescence that should be cited or discussed. For every citation you consider wrong, misattributed or misrepresented, verify it (DOI, authors, year, what the paper actually says) before reporting it, and say how you verified it. Do not invent references; if you are not sure a paper exists, say so.
6. Overclaiming and framing: any sentence that overstates evidence, implies causality, or uses alarmist language; equally, any place where a null result is presented as stronger evidence of absence than the stated upper bounds allow.
7. Clarity and structure: readability, figure and table quality, terminology (e.g. "ETAS residual background"), length, what could be moved to a supplement.

Format of your answer:
- A short summary (5-8 sentences) with your overall assessment and a recommendation (accept / minor / major revision / reject) as if for a journal.
- Section A, "Errors": things that are wrong (statistical, physical, numerical, citation errors, internal inconsistencies). For each: location (section/table/figure), what is wrong, why, and the concrete fix.
- Section B, "Suggestions": improvements that are not errors (additional analyses, literature, wording, presentation).
- Section C, "Prioritised fix list": a numbered list of concrete changes ordered by importance (must fix before submission / should fix / nice to have).
Keep errors and suggestions strictly separate, and mark your confidence (high / medium / low) for each item.
