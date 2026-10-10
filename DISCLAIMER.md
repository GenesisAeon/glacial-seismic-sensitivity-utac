# DISCLAIMER – Tests, not forecasts; no framework bridge

> **Why no UTAC/CREP/AFET bridge:** as in P101 (`glacial-seismicity-utac`), deliberately. Climate and
> earthquake questions should stay accessible and checkable without the GenesisAeon framework
> vocabulary. See the canonical note in `PACKAGE_REGISTRY.md` ("Why no UTAC/CREP/AFET bridge in the
> climate/ecology series", 2026-08-31) in the GenesisAeon workspace root.

**Status:** statistical tests on public earthquake catalogues and GRACE loads. Results are reported as
computed, including non-significant ones. Nothing here is a hazard assessment.

## What this package is

- A set of retrospective tests (1990–2025) of whether seismicity near melting glaciers has become more
  sensitive to the seasonal unloading. These tests were specified after exploratory contact with the
  same data and are labelled accordingly.
- A pre-registered confirmatory test on data from 2026-11-01 on, frozen on 2026-10-10.
- An order-of-magnitude model of delayed (viscous) responses with viscosities from the literature.

## What this package is NOT

- **Not a forecast** of earthquakes or eruptions for any city or region. The lag-model curves are
  scenarios with an unknown coupling factor κ, not predictions.
- **Not a hazard map.** Counting small earthquakes says little about single large ruptures on critically
  stressed faults.
- **Not evidence that glacier melt is harmless.** A flat trend does not exclude a delayed response
  (`honesty.does_flat_trend_exclude_delayed_response()` → `False`).
- **Not evidence that glacier melt raises earthquake hazard** at the present time. No test of growing
  sensitivity is significant after multiple-testing correction.
- **Not a volcanic study.** Decompression melting under Icelandic ice caps (Maclennan et al. 2002;
  Schmidt et al. 2013) is discussed only as context.

## Verification

All 33 DOIs in `constants.py` and `docs/SOURCES.md` resolve via Crossref (`python scripts/verify_dois.py`, 2026-10-10).
Values taken only from abstracts are marked *(Abstract)* in [docs/SOURCES.md](docs/SOURCES.md).
During verification, one DOI (Loomis et al. 2019) and three titles were corrected before use.
