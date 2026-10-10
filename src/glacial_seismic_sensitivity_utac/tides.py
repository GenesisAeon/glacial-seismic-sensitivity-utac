"""Solid-earth (body) tide phase of earthquakes, Schuster test and tidal b-value split (v0.2, M3).

Scope and limitations (also in docs/METHODS_v02.md):
* Low-precision lunar/solar ephemeris (main periodic terms of Meeus, *Astronomical Algorithms*,
  2nd ed., ch. 25 and 47); accuracy ~0.02 deg in position, ~0.01 % in distance - ample for
  the degree-2 tidal potential (relative error << 1 %).
* Only the degree-2 **body tide** is modelled (Love numbers h = 0.6114, l = 0.0832 as frozen in
  PREREGISTRATION_v0.2; no citable source was found for this pair. The IERS Conventions 2010
  nominal degree-2 values (Petit & Luzum 2010, IERS TN 36, ch. 7, eq. 7.5: h = 0.6078,
  l = 0.0847; LOVE_H_IERS2010 / LOVE_L_IERS2010) give a 2.2 % smaller strain and *identical
  phases*, so the preregistered Schuster and b-value tests do not depend on the choice;
  amplitudes are also reported with the IERS values);
  the horizontal areal strain at the surface is (2h - 6l) W2 / (g a), tension positive.
* **Ocean loading is NOT included.** In coastal regions (SE Alaska, NZ, Iceland, Greenland) the
  load tide can be comparable to or larger than the body tide and has a different phase. A
  null result here therefore does not exclude tidal triggering by the full (body + load) tide.
* Phase convention after Tanaka, Ohtake & Sato (2002, JGR 107(B10):2211,
  doi:10.1029/2001JB001577): 0 deg at a strain maximum,
  +/-180 deg at minima, linearly interpolated in time between consecutive extrema.
* Time scale: catalogue times are UTC decimal years; TD - UT (~1 min) is ignored.
"""

from __future__ import annotations

import numpy as np
from scipy import stats

DEG = np.pi / 180.0
GM_MOON = 4.9028e12  # m^3 s^-2
GM_SUN = 1.32712440018e20
A_EARTH = 6.371e6  # m (mean radius)
G_SURF = 9.81
AU = 1.495978707e11
LOVE_H = 0.6114
LOVE_L = 0.0832
LOVE_H_IERS2010 = 0.6078  # IERS TN 36 (2010), ch. 7, step-1 nominal h(0)
LOVE_L_IERS2010 = 0.0847  # IERS TN 36 (2010), ch. 7, step-1 nominal l(0)
STRAIN_FACTOR_IERS2010 = 2 * LOVE_H_IERS2010 - 6 * LOVE_L_IERS2010  # 0.7074
STRAIN_FACTOR = 2 * LOVE_H - 6 * LOVE_L  # 0.7236


def decyear_to_jd(t: np.ndarray) -> np.ndarray:
    """Decimal year (as produced by catalog.py, Gregorian) -> Julian date."""
    t = np.asarray(t, float)
    y = np.floor(t)
    jd0 = _jd_jan1(y)
    jd1 = _jd_jan1(y + 1)
    return np.asarray(jd0 + (t - y) * (jd1 - jd0))


def _jd_jan1(y: np.ndarray) -> np.ndarray:
    y = np.asarray(y, float) - 1
    a = np.floor(y / 100)
    b = 2 - a + np.floor(a / 4)
    return np.asarray(np.floor(365.25 * (y + 4716)) + np.floor(30.6001 * 14) + 1 + b - 1524.5)


def moon_ecliptic(jd: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Geocentric ecliptic longitude, latitude [deg] and distance [km] of the Moon."""
    T = (np.asarray(jd, float) - 2451545.0) / 36525.0
    Lp = 218.3164477 + 481267.88123421 * T
    D = (297.8501921 + 445267.1114034 * T) * DEG
    M = (357.5291092 + 35999.0502909 * T) * DEG
    Mp = (134.9633964 + 477198.8675055 * T) * DEG
    F = (93.2720950 + 483202.0175233 * T) * DEG
    s = np.sin
    cs = np.cos
    lon = (
        6288774 * s(Mp)
        + 1274027 * s(2 * D - Mp)
        + 658314 * s(2 * D)
        + 213618 * s(2 * Mp)
        - 185116 * s(M)
        - 114332 * s(2 * F)
        + 58793 * s(2 * D - 2 * Mp)
        + 57066 * s(2 * D - M - Mp)
        + 53322 * s(2 * D + Mp)
        + 45758 * s(2 * D - M)
        - 40923 * s(M - Mp)
        - 34720 * s(D)
        - 30383 * s(M + Mp)
        + 15327 * s(2 * D - 2 * F)
        - 12528 * s(Mp + 2 * F)
        + 10980 * s(Mp - 2 * F)
        + 10675 * s(4 * D - Mp)
        + 10034 * s(3 * Mp)
        + 8548 * s(4 * D - 2 * Mp)
        - 7888 * s(2 * D + M - Mp)
        - 6766 * s(2 * D + M)
        - 5163 * s(D - Mp)
        + 4987 * s(D + M)
        + 4036 * s(2 * D - M + Mp)
    ) * 1e-6
    lat = (
        5128122 * s(F)
        + 280602 * s(Mp + F)
        + 277693 * s(Mp - F)
        + 173237 * s(2 * D - F)
        + 55413 * s(2 * D - Mp + F)
        + 46271 * s(2 * D - Mp - F)
        + 32573 * s(2 * D + F)
        + 17198 * s(2 * Mp + F)
        + 9266 * s(2 * D + Mp - F)
        + 8822 * s(2 * Mp - F)
        + 8216 * s(2 * D - M - F)
        + 4324 * s(2 * D - 2 * Mp - F)
        + 4200 * s(2 * D + Mp + F)
    ) * 1e-6
    r = 385000.56 + 1e-3 * (
        -20905355 * cs(Mp)
        - 3699111 * cs(2 * D - Mp)
        - 2955968 * cs(2 * D)
        - 569925 * cs(2 * Mp)
        + 48888 * cs(M)
        - 3149 * cs(2 * F)
        + 246158 * cs(2 * D - 2 * Mp)
        - 152138 * cs(2 * D - M - Mp)
        - 170733 * cs(2 * D + Mp)
        - 204586 * cs(2 * D - M)
        - 129620 * cs(M - Mp)
        + 108743 * cs(D)
        + 104755 * cs(M + Mp)
        + 10321 * cs(2 * D - 2 * F)
        + 79661 * cs(Mp - 2 * F)
        - 34782 * cs(4 * D - Mp)
        - 23210 * cs(3 * Mp)
        - 21636 * cs(4 * D - 2 * Mp)
    )
    return np.asarray(np.mod(Lp + lon, 360.0)), np.asarray(lat), np.asarray(r)


def sun_ecliptic(jd: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Geometric ecliptic longitude [deg] and distance [AU] of the Sun (Meeus ch. 25)."""
    T = (np.asarray(jd, float) - 2451545.0) / 36525.0
    L0 = 280.46646 + 36000.76983 * T + 0.0003032 * T**2
    M = 357.52911 + 35999.05029 * T - 0.0001537 * T**2
    e = 0.016708634 - 0.000042037 * T
    Mr = M * DEG
    C = (
        (1.914602 - 0.004817 * T) * np.sin(Mr)
        + (0.019993 - 0.000101 * T) * np.sin(2 * Mr)
        + 0.000289 * np.sin(3 * Mr)
    )
    nu = (M + C) * DEG
    R = 1.000001018 * (1 - e**2) / (1 + e * np.cos(nu))
    return np.asarray(np.mod(L0 + C, 360.0)), np.asarray(R)


def _ecl_to_unit_itrf(lon: np.ndarray, lat: np.ndarray, jd: np.ndarray) -> np.ndarray:
    T = (jd - 2451545.0) / 36525.0
    eps = (23.439291 - 0.0130042 * T) * DEG
    lo, la = lon * DEG, lat * DEG
    x = np.cos(la) * np.cos(lo)
    y = np.cos(la) * np.sin(lo)
    z = np.sin(la)
    ye = y * np.cos(eps) - z * np.sin(eps)
    ze = y * np.sin(eps) + z * np.cos(eps)
    gmst = np.mod(280.46061837 + 360.98564736629 * (jd - 2451545.0), 360.0) * DEG
    xr = x * np.cos(gmst) + ye * np.sin(gmst)
    yr = -x * np.sin(gmst) + ye * np.cos(gmst)
    return np.stack([xr, yr, ze], axis=-1)


def _site_unit(lat: np.ndarray, lon: np.ndarray) -> np.ndarray:
    la, lo = np.asarray(lat, float) * DEG, np.asarray(lon, float) * DEG
    return np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], axis=-1)


def tidal_potential_w2(jd: np.ndarray, lat: np.ndarray, lon: np.ndarray) -> np.ndarray:
    """Degree-2 tide-generating potential W2 [m^2 s^-2] of Moon + Sun at the surface."""
    jd = np.asarray(jd, float)
    site = _site_unit(np.broadcast_to(lat, jd.shape), np.broadcast_to(lon, jd.shape))
    ml, mb, mr = moon_ecliptic(jd)
    sl, sr = sun_ecliptic(jd)
    out = np.zeros_like(jd)
    for gm, lo, la, r in ((GM_MOON, ml, mb, mr * 1e3), (GM_SUN, sl, np.zeros_like(sl), sr * AU)):
        u = _ecl_to_unit_itrf(lo, la, jd)
        cpsi = np.sum(u * site, axis=-1)
        out += gm * A_EARTH**2 / r**3 * 0.5 * (3 * cpsi**2 - 1)
    return out


def areal_strain(jd: np.ndarray, lat: np.ndarray, lon: np.ndarray) -> np.ndarray:
    """Horizontal areal body-tide strain at the surface (dimensionless, tension positive)."""
    return np.asarray(STRAIN_FACTOR * tidal_potential_w2(jd, lat, lon) / (G_SURF * A_EARTH))


def tidal_phase(
    t_decyr: np.ndarray,
    lat: np.ndarray,
    lon: np.ndarray,
    half_window_h: float = 14.0,
    step_min: float = 5.0,
    chunk: int = 2000,
) -> tuple[np.ndarray, np.ndarray]:
    """Tanaka-type phase [deg, -180..180] and strain amplitude at each event (local site)."""
    jd = decyear_to_jd(np.asarray(t_decyr, float))
    lat = np.broadcast_to(np.asarray(lat, float), jd.shape)
    lon = np.broadcast_to(np.asarray(lon, float), jd.shape)
    off = np.arange(-half_window_h * 60, half_window_h * 60 + step_min, step_min) / 1440.0
    k0 = int(np.argmin(np.abs(off)))
    phase = np.full(jd.shape, np.nan)
    amp = np.full(jd.shape, np.nan)
    for s in range(0, len(jd), chunk):
        sl = slice(s, s + chunk)
        J = jd[sl, None] + off[None, :]
        E = areal_strain(J, lat[sl, None], lon[sl, None])
        amp[sl] = areal_strain(jd[sl], lat[sl], lon[sl])
        d = np.diff(E, axis=1)
        sgn = np.sign(d)
        # extremum at sample k if slope changes sign between k-1 and k
        ext = np.zeros_like(E, dtype=int)
        ext[:, 1:-1] = np.where(
            (sgn[:, :-1] > 0) & (sgn[:, 1:] <= 0),
            1,
            np.where((sgn[:, :-1] < 0) & (sgn[:, 1:] >= 0), -1, 0),
        )
        for r in range(E.shape[0]):
            ks = np.nonzero(ext[r])[0]
            prev = ks[ks <= k0]
            nxt = ks[ks > k0]
            if len(prev) == 0 or len(nxt) == 0:
                continue
            a, b = prev[-1], nxt[0]
            frac = (off[k0] - off[a]) / (off[b] - off[a])
            if ext[r, a] == 1 and ext[r, b] == -1:
                phase[s + r] = 180.0 * frac
            elif ext[r, a] == -1 and ext[r, b] == 1:
                phase[s + r] = -180.0 + 180.0 * frac
    return phase, amp


def schuster(phase_deg: np.ndarray) -> dict[str, float]:
    """Schuster test p = exp(-R^2/N); amplitude a_hat = 2R/N for rate ~ 1 + a cos(theta)."""
    th = np.asarray(phase_deg, float)
    th = th[np.isfinite(th)] * DEG
    n = len(th)
    if n == 0:
        return dict(n=0.0, R=np.nan, p=np.nan, a_hat=np.nan, mean_phase_deg=np.nan)
    z = np.sum(np.exp(1j * th))
    R = float(abs(z))
    return dict(
        n=float(n),
        R=R,
        p=float(np.exp(-(R**2) / n)),
        a_hat=2 * R / n,
        mean_phase_deg=float(np.angle(z) / DEG),
    )


def sample_modulated_phases(
    n: int, a: float, rng: np.random.Generator, phi0_deg: float = 0.0
) -> np.ndarray:
    """Phases from density (1 + a cos(theta - phi0)) / (2 pi), 0 <= a <= 1 (rejection)."""
    out = np.empty(0)
    while len(out) < n:
        th = rng.uniform(-np.pi, np.pi, 2 * n)
        keep = rng.uniform(0, 1 + a, 2 * n) < 1 + a * np.cos(th - phi0_deg * DEG)
        out = np.concatenate([out, th[keep]])
    return np.asarray(out[:n] / DEG)


def schuster_mde(
    n: int,
    alpha: float = 0.05,
    power: float = 0.8,
    n_sim: int = 400,
    rng: np.random.Generator | None = None,
) -> float:
    """Smallest modulation amplitude a detected with given power (simulation, bisection)."""
    rng = rng or np.random.default_rng(0)
    if n < 10:
        return float("nan")

    def pw(a: float) -> float:
        hits = 0
        for _ in range(n_sim):
            hits += schuster(sample_modulated_phases(n, a, rng))["p"] < alpha
        return hits / n_sim

    lo, hi = 0.0, 1.0
    for _ in range(12):
        mid = 0.5 * (lo + hi)
        if pw(mid) >= power:
            hi = mid
        else:
            lo = mid
    return hi


# ---------------------------------------------------------------------------
# b-value split
# ---------------------------------------------------------------------------
def b_mle(m: np.ndarray, mc: float, dm: float = 0.1) -> tuple[float, float]:
    """Aki-Utsu b-value with binning correction and Shi & Bolt (1982) standard error."""
    m = np.asarray(m, float)
    m = m[m >= mc - 1e-9]
    n = len(m)
    if n < 2:
        return float("nan"), float("nan")
    b = np.log10(np.e) / (m.mean() - (mc - dm / 2))
    se = 2.3 * b**2 * np.sqrt(np.sum((m - m.mean()) ** 2) / (n * (n - 1)))
    return float(b), float(se)


def _gr_loglik(m: np.ndarray, mc: float, b: float, dm: float) -> float:
    beta = b * np.log(10)
    x = m - (mc - dm / 2)
    return float(len(m) * np.log(beta) - beta * np.sum(x))


def b_split_test(
    m: np.ndarray, phase_deg: np.ndarray, mc: float, dm: float = 0.1
) -> dict[str, float]:
    """b in the tensile half (|phase| < 90) vs compressive half; LR test (chi2, 1 dof),
    two-sided p and one-sided p for b_tensile < b_compressive (direction as in Tan et al. 2019,
    EPSL 512:39, doi:10.1016/j.epsl.2019.01.047)."""
    m = np.asarray(m, float)
    ph = np.asarray(phase_deg, float)
    ok = np.isfinite(ph) & (m >= mc - 1e-9)
    m, ph = m[ok], ph[ok]
    hi = np.abs(ph) < 90
    m1, m2 = m[hi], m[~hi]
    if len(m1) < 20 or len(m2) < 20:
        return dict(
            n_tens=float(len(m1)),
            n_comp=float(len(m2)),
            b_tens=np.nan,
            b_comp=np.nan,
            d_b=np.nan,
            p_two=np.nan,
            p_one=np.nan,
        )
    b1, s1 = b_mle(m1, mc, dm)
    b2, s2 = b_mle(m2, mc, dm)
    b0, _ = b_mle(m, mc, dm)
    lr = 2 * (_gr_loglik(m1, mc, b1, dm) + _gr_loglik(m2, mc, b2, dm) - _gr_loglik(m, mc, b0, dm))
    p_two = float(stats.chi2.sf(max(lr, 0.0), 1))
    z = (b1 - b2) / np.hypot(s1, s2)
    return dict(
        n_tens=float(len(m1)),
        n_comp=float(len(m2)),
        b_tens=b1,
        b_comp=b2,
        se_tens=s1,
        se_comp=s2,
        d_b=b1 - b2,
        lr=float(lr),
        p_two=p_two,
        p_one=float(stats.norm.cdf(z)),
    )


def db_mde(
    n: int,
    b: float = 1.0,
    alpha: float = 0.05,
    power: float = 0.8,
    n_sim: int = 300,
    rng: np.random.Generator | None = None,
    mc: float = 2.0,
) -> float:
    """Smallest |Delta b| (tensile lower) detected one-sided with given power, n split ~ 50/50."""
    rng = rng or np.random.default_rng(1)
    if n < 40:
        return float("nan")

    def pw(db: float) -> float:
        hits = 0
        for _ in range(n_sim):
            n1 = n // 2
            m1 = mc - 0.05 + rng.exponential(1 / ((b - db) * np.log(10)), n1)
            m2 = mc - 0.05 + rng.exponential(1 / (b * np.log(10)), n - n1)
            m_all = np.round(np.concatenate([m1, m2]) / 0.1) * 0.1
            ph = np.concatenate([np.zeros(n1), np.full(n - n1, 180.0)])
            hits += b_split_test(m_all, ph, mc)["p_one"] < alpha
        return hits / n_sim

    lo, hi = 0.0, 0.6
    for _ in range(10):
        mid = 0.5 * (lo + hi)
        if pw(mid) >= power:
            hi = mid
        else:
            lo = mid
    return hi
