# Gemini Deep Research prompt – P133 v0.3 (mass-change / collapse seismicity)

Status: draft, 2026-10-11. Paste the text below into Gemini Deep Research. Results are an
idea and literature source only; every number or citation must be checked against the primary
source before it enters the repository.

---

## Context

I am an independent researcher working on the open project **glacial-seismic-sensitivity-utac
(P133)**, https://github.com/GenesisAeon/glacial-seismic-sensitivity-utac (Zenodo:
https://doi.org/10.5281/zenodo.23281091 for v0.1.0 and https://doi.org/10.5281/zenodo.23286492
for v0.2.0). Up to v0.2 the project tests whether seismicity in glaciated regions is becoming
more sensitive to (un)loading: seasonal modulation, load sensitivity per kPa from GRACE,
a time-varying ETAS background, tidal-phase tests, a viscoelastic lag model with rate-and-state
seismicity, tipping scenarios and a preregistered prospective test. Results so far are null or
non-robust, reported with upper bounds.

Version 0.3 is planned as a module on **seismicity driven by mass change and cavity or
reservoir collapse**. The motivating analogue is the Punggye-ri nuclear test site (DPRK):
repeated underground explosions, a collapse event minutes after the September 2017 test,
subsequent subsidence and lingering small seismicity. The question is where on Earth natural or
anthropogenic mass changes, voids and pressurised volumes can produce comparable signatures,
how to recognise them, and whether any of this couples to regions of present-day ice loss.

Candidate calibration/control cases I already have in mind (please verify, correct or replace):
Groningen gas field (Netherlands), Koyna–Warna reservoirs (India), Lorca 2011 (Spain,
groundwater extraction), Punggye-ri post-test collapse (2017), Bárðarbunga 2014–15 caldera
collapse (Iceland), the Langtang valley avalanche/landslide of the 2015 Gorkha earthquake, and a
flash flood reported on 11 October 2026 in the Budhi Gandaki valley (Gorkha district, Nepal),
possibly from a landslide-dam breach near Chumchet. For the last event I have no verified
information: please establish whether it happened, what is documented, and whether any seismic
or infrasound signal was recorded; if nothing reliable exists, say so explicitly.

## Research questions

1. **Where are such effects plausible?** For each setting give the physical preconditions and
   the regions where they are met, with examples:
   magma chambers and magma flow; calderas (piston collapse); natural gas, oil and CO2 reservoirs;
   methane hydrates and gas pockets (including submarine and permafrost settings); karst and
   other natural cavities; permafrost thaw and thermokarst; subglacial and proglacial lakes and
   outburst floods; artificial reservoirs and groundwater depletion; mines, salt caverns and
   underground explosion sites; pre-stressed faults near rapid ice loss (e.g. SE Alaska,
   Iceland, Patagonia, Greenland, Antarctica, Alps, Himalaya, New Zealand).
2. **Case catalogue.** Documented cases of seismicity caused or modulated by mass removal,
   mass addition, pressure change or cavity collapse. For each: location, mechanism, forcing
   (volume/mass/pressure change and its rate), largest magnitude, number of events, onset delay
   and duration (timescales from seconds to decades), focal mechanism / moment tensor
   (including non-double-couple components), geodetic signal (InSAR/GNSS subsidence or uplift),
   key references with DOIs, and the open data sources (catalogues, waveforms, InSAR, GNSS,
   production/injection or water-level records).
3. **Physical mechanisms.** Explain and compare: poroelastic stress and pore-pressure diffusion;
   Coulomb stress change from unloading or loading; cavity roof collapse and chimney formation;
   caldera piston collapse and ring-fault slip; reservoir compaction; gas-hydrate dissociation
   and slope failure; interplay with glacial isostatic rebound and with seasonal/hydrological
   loading. Give typical stress changes (kPa–MPa), length scales and time constants, and where
   these mechanisms interact or cascade.
4. **How to model reliably.** Which methods are appropriate for which question, with their
   limitations and the open tools that implement them: Coulomb stress transfer (e.g. Coulomb
   3, PSCMP/PSGRN), poroelastic and thermo-poroelastic models, rate-and-state seismicity
   (Dieterich), ETAS and other point processes with external forcing (time-varying background,
   forcing-driven productivity), finite-element models (e.g. PyLith and others), moment-tensor
   inversion with isotropic/CLVD terms (e.g. ISOLA, MTfit, Grond or comparable), InSAR time
   series (e.g. LiCSBAS, MintPy, ISCE), GNSS time series. Include minimum data requirements
   and known pitfalls (non-uniqueness of non-DC solutions, velocity-model trade-offs, catalogue
   incompleteness after large events).
5. **Discrimination from tectonic background.** Which observables separate collapse or
   mass-change seismicity from ordinary tectonic seismicity: moment-tensor decomposition
   (implosive isotropic, CLVD), first-motion polarity, depth, spectral/source-time-function
   characteristics, Omori versus non-Omori decay, b-value, spatial migration and diffusion
   fronts, correlation with forcing time series, coincident subsidence. Give published
   discrimination criteria and their reported success/error rates where available.
6. **Calibration cases.** Rank the documented cases by suitability for calibrating a
   discrimination and forcing–response model: known and quantified forcing, open high-quality
   data, independent geodesy, clear onset. Give 5–10 recommended cases with reasons and the
   exact datasets.
7. **Cascades and coupling to glacial unloading.** Where could ice loss interact with the
   settings above (e.g. unloading of magma systems, glacier-dammed and moraine lakes, permafrost
   slopes, hydrate stability under changing pressure/temperature, reservoirs near glaciers),
   especially near population centres? Separate documented cases from hypotheses, and for each
   hypothesis state what observation would support or refute it.
8. **Upper bounds and null approaches.** How have studies quantified the absence of an effect
   (minimum detectable effect, power analysis, control regions, synthetic catalogues,
   preregistration)? Which designs would allow a credible null result for collapse or
   mass-change seismicity in glaciated regions?
9. **Overlooked phenomena and emergent links.** Phenomena or connections that are rarely
   discussed but physically plausible and testable with open data. Label these clearly as
   speculative.

## Requirements for the answer

- **Citations:** only real, verifiable sources. Give DOIs for papers and stable URLs for data
  and software. Verify each DOI resolves to the cited paper. If you cannot verify a source, say
  "unverified" and do not use it to support a number.
- **Uncertainty labels:** mark every quantitative statement as *established* (multiple
  independent studies), *reported* (single study), or *speculative* (hypothesis, analogy).
- **Separate** established knowledge, reported single cases, and speculation in distinct
  sections or columns.
- **No alarmism:** describe hazards soberly with magnitudes, probabilities or rates where known;
  do not extrapolate single cases to global claims.
- **Numbers:** give units, ranges and the source for each number; do not round away
  uncertainty.

## Output format

1. Executive summary (max. 1 page).
2. Table A – settings and regions where mass-change/collapse seismicity is plausible
   (setting, preconditions, example regions, typical magnitudes and timescales, evidence level).
3. Table B – case catalogue (case, location, years, mechanism, forcing, Mmax, N events,
   onset delay/duration, moment-tensor type, geodesy, data sources, key DOIs, evidence level).
4. Table C – datasets and tools (name, content, coverage, access URL, licence, suitability).
5. Ranked list of calibration cases (5–10) with justification.
6. Discrimination criteria table (observable, criterion, reported performance, references).
7. Modelling recommendations: which model for which question, minimum data, pitfalls.
8. Cascades and coupling to glacial unloading: documented vs hypothetical, each with a
   falsifiable test.
9. Upper-bound / null-result design recommendations.
10. Overlooked phenomena (speculative, clearly marked).
11. Full reference list with DOIs/URLs and a note on how each was verified.
