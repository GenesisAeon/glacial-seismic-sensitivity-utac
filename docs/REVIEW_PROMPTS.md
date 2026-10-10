# Review-Prompts für v0.2 (PR #1)

PR: https://github.com/GenesisAeon/glacial-seismic-sensitivity-utac/pull/1 (Branch `v0.2-dev`).
Jeder Prompt ist zum direkten Einfügen gedacht. Bitte keine Merges, Tags oder Releases durch die
Reviewer. Antworten bitte als Liste von Befunden mit Datei/Zeile, Schweregrad (blockierend /
wichtig / klein) und konkretem Änderungsvorschlag.

---

## 1. Claude Code – Code-Review

```
Review PR https://github.com/GenesisAeon/glacial-seismic-sensitivity-utac/pull/1 (branch v0.2-dev)
of the Python package glacial-seismic-sensitivity-utac. Do NOT merge, tag or release.

Scope (new/changed code):
- src/glacial_seismic_sensitivity_utac/etas_nonstat.py  (nonstationary ETAS: likelihood, analytic
  gradient, two-stage estimator, covariance, simulate, mu_window_mle, did_test, bh_adjust)
- tides.py (Meeus-based Moon/Sun ephemeris, degree-2 body-tide strain, Tanaka phase, Schuster,
  b-value split, MDE simulations)
- robustness_mc.py (Ogata-Katsura EMR Mc, bootstrap, Gardner-Knopoff)
- lag_sensitivity.py and the new optional `rheologies` argument of tipping.run_scenarios
- confirmatory_v02.py, v02.py (orchestrator, checkpoints), plots_v02.py, cli.py (`v02` subcommand)
- tests/test_etas_nonstat.py, test_tides.py, test_robustness_mc.py, test_lag_sensitivity.py,
  test_v02_prereg.py; scripts/v02_*.py

Please check in particular:
1. Correctness of the ETAS log-likelihood and gradient (kernel truncated at tmax, events before t0
   only as triggers, bins), and whether the covariance for fix_trig (mu block only) is right.
2. The simulator (`simulate`): Omori inverse-CDF sampling, magnitude rounding, edge effects.
3. `tidal_phase`: extremum detection, phase interpolation, behaviour at window edges (NaNs).
4. `gardner_knopoff`: window logic (foreshocks and aftershocks, decreasing magnitude).
5. That v0.1.0 behaviour is unchanged (tipping.run_scenarios default, frozen JSON hashes).
6. Numerical robustness (p at its lower bound 1.0001 in most regions, overflow, RAM: the box has
   ~3 GB free; pair arrays are held in memory).
7. Test quality: are the synthetic recovery tests meaningful and not flaky? Missing tests?
8. mypy --strict / ruff cleanliness and CI (Python 3.11/3.12; numpy>=1.26 lower bound).
```

## 2. Astra – Theorie-Review

```
You are reviewing the scientific reasoning of v0.2 of glacial-seismic-sensitivity-utac,
PR https://github.com/GenesisAeon/glacial-seismic-sensitivity-utac/pull/1. Read
PREREGISTRATION_v0.2.md, docs/METHODS_v02.md, docs/v02_benchmarks.md, the v0.2 section of
docs/RESULTS.md and docs/LIMITATIONS.md.

Questions:
1. Is a temporal ETAS with yearly piecewise-constant background and a two-stage estimator
   (stationary triggering parameters, then yearly mu) a defensible way to separate a forcing-driven
   background change from aftershock decay? What biases follow from tmax = 1 yr and p at its lower
   bound (1.0001) in 7 of 8 regions?
2. The preregistered H2.1 is formally significant (SE Alaska minus Interior Alaska, +0.41 +/- 0.14
   per decade, p = 0.0017) but disappears from 2003 on. Is our reading (network-history artefact)
   the most plausible one? What else could produce it?
3. The "masked background rise" (deceptive-quiet) classification: are the rules sensible? Is the
   null finding informative given the power?
4. Body-tide only (no ocean loading): how strongly does this limit the interpretation in SE Alaska,
   New Zealand, Iceland and Greenland? Is the areal-strain proxy (2h-6l) W2/(g a) adequate?
5. Lag model with Sasgen et al. 2026 viscosities: is it consistent to use their lithosphere thickness
   as Te of a thin-plate filter and their asthenosphere viscosity as a half-space viscosity? The
   result that the earliest detection year depends on the elastic fraction rather than viscosity –
   physically reasonable or model artefact?
6. Is the prospective test C2 (log mu change from 2027-01-01 with frozen triggering parameters,
   glacier minus control) well posed? Any loophole in the SE formula?
Keep to physics and statistics; flag over-interpretation. Sober language.
```

## 3. Gemini – enge Literaturprüfung

```
Narrow literature check for PR https://github.com/GenesisAeon/glacial-seismic-sensitivity-utac/pull/1.
Verify ONLY the following citations and numbers against the original papers (give the exact page,
table or figure; say "not found" if you cannot verify; do not add new claims or new sources unless
a cited statement is wrong):
1. Sasgen et al. 2026, Commun. Earth Environ. 7:518, doi:10.1038/s43247-026-03738-y: Alaska
   preferred asthenosphere viscosity 3e18 Pa s with lithosphere thickness 30 km; Iceland 1e18 Pa s,
   30 km (GNSS fit 40 km); ensemble 1e18-3e19 Pa s and 30-90 km.
2. Kumazawa & Ogata 2013, JGR 118:6165, doi:10.1002/2013JB010259 (nonstationary ETAS) - is our
   simplified yearly-bin version a fair description of "the idea"?
3. Tanaka, Ohtake & Sato 2002, JGR 107(B10):2211, doi:10.1029/2001JB001577 - phase convention
   (0 deg at maximum, +/-180 deg at minima).
4. Tan, Waldhauser, Tolstoy & Wilcock 2019, EPSL 512:39-45, doi:10.1016/j.epsl.2019.01.047 -
   b value lower at higher tidal stress (direction only).
5. Ogata & Katsura 1993, GJI 113:727, doi:10.1111/j.1365-246X.1993.tb04663.x - detection function
   Phi((m-mu)/sigma) times Gutenberg-Richter.
6. Gardner & Knopoff 1974 windows as given by van Stiphout, Zhuang & Marsan 2012 (CORSSA,
   doi:10.5078/corssa-52382934): L = 10^(0.1238M+0.983) km, T = 10^(0.032M+2.7389) d (M >= 6.5)
   else 10^(0.5409M-0.547) d.
7. IPCC AR6 WG I SPM A.1.7: global mean sea-level rise 3.7 mm/yr (2006-2018).
8. Love numbers h2 = 0.6114, l2 = 0.0832 used in tides.py: give a citable source, or confirm that
   the IERS Conventions 2010 nominal values (h2 = 0.6078, l2 = 0.0847) should be preferred
   (affects only the strain amplitude, not the phases).
Output: a table claim | verified? | exact location | correction.
```

## 4. Grok – Präregistrierungs-Gegenprüfung

```
Cross-check the preregistration of v0.2 in PR
https://github.com/GenesisAeon/glacial-seismic-sensitivity-utac/pull/1.
Files: PREREGISTRATION_v0.2.md, results/frozen_v02_preregistration.json,
results/frozen_v02_baselines.json, results/frozen_confirmatory_parameters.json and
results/frozen_monitoring_indicators.json (v0.1.0), tests/test_v02_prereg.py, the git history of
branch v0.2-dev (commit fa4a077 = preregistration, 250457c = results).

Check:
1. Was the preregistration committed and pushed before the real-data analyses it governs (compare
   commit times and the 'created' field of the baselines; results/v02/v02_run.log is not committed,
   so rely on git)? Is anything in the results commit inconsistent with the frozen rules (estimator,
   tmax, SE factor 1.25, windows, pairs, BH, classes)?
2. Are the SHA-256 values in the document, the JSON and the tests consistent, and are the v0.1.0
   frozen files byte-identical to v0.1.0 (tag v0.1.0)?
3. Is C2 fully specified (data window from 2027-01-01, looks and alphas, statistic, SE, catalogue
   rules, baselines) so that someone else could run it in 2030 without choices left open?
   List every remaining degree of freedom.
4. Are H2/H3 honestly labelled as retrospective and the exploratory H2.1 checks clearly separated
   from the preregistered result in docs/RESULTS.md?
5. Zenodo: the addendum is not yet archived (needs a release); what is the minimum to do before
   2027-01-01?
Report discrepancies only, with file and line.
```
