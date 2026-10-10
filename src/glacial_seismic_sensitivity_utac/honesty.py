"""Explicit negative claims (GenesisAeon convention). Each function documents a statement the
package must NOT be read as making."""

from __future__ import annotations


def is_seasonal_alaska_signal_novel() -> bool:
    """Johnson, Fu & Buergmann 2020 (doi:10.1016/j.epsl.2019.115904) already showed hydrospheric
    seasonal modulation of southern Alaskan seismicity (3.5 %/kPa). We replicate it.
    Always False."""
    return False


def does_flat_trend_exclude_delayed_response() -> bool:
    """A flat 1990-2025 trend says nothing about a viscously delayed response (relaxation times of
    decades to millennia). Always False."""
    return False


def is_growing_sensitivity_the_generic_rate_state_expectation() -> bool:
    """For periods >> t_a, rate-and-state predicts seasonal modulation ~ 2 pi dS/(T Sdot); added
    GIA stressing *lowers* it. Growth needs e.g. falling effective normal stress or approach to
    failure. Always False."""
    return False


def is_lag_model_a_forecast() -> bool:
    """The lag model is a scenario calculator with an unconstrained load-to-fault-stress factor
    kappa and assumed load wavelengths. Always False."""
    return False


def are_retrospective_1990_2025_tests_preregistered() -> bool:
    """The Fruehstadium hypotheses were written after Phase-2 exploration of the same data; only the
    confirmatory test on data from 2026-11-01 onward is pre-registered in the strict sense.
    Always False."""
    return False


def does_rain_vs_ice_separation_succeed_in_se_alaska() -> bool:
    """GRACE unloading and ERA5 rain/snow anomalies are correlated (|r| ~ 0.7 in SE Alaska) -
    model comparison cannot cleanly attribute the seasonal signal. Always False."""
    return False


def does_this_package_predict_earthquakes_or_eruptions() -> bool:
    """No. Always False."""
    return False
