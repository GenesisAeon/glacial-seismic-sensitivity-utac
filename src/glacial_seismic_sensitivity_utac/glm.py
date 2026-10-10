"""Minimal Poisson GLM with group (year) fixed effects, fitted by IRLS, quasi-Poisson errors.

Year fixed effects absorb any year-to-year change of the overall rate -- including catalogue
changes such as network densification -- so that the remaining regressors only measure
*within-year* (seasonal) contrasts.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import stats


@dataclass
class GLMResult:
    coef: np.ndarray  # regressor coefficients (fixed effects excluded)
    se: np.ndarray  # quasi-Poisson standard errors
    phi: float  # Pearson dispersion
    llf: float  # Poisson log-likelihood
    n: int
    k: int  # total number of parameters incl. fixed effects
    mu: np.ndarray

    def z(self) -> np.ndarray:
        return np.asarray(self.coef / self.se)

    def p_one_sided(self, i: int) -> float:
        """P(Z >= z_i) - pre-registered direction 'coefficient > 0'."""
        return float(stats.norm.sf(self.z()[i]))

    def p_two_sided(self, i: int) -> float:
        return float(2 * stats.norm.sf(abs(self.z()[i])))

    def qaic(self, phi_ref: float) -> float:
        return float(-2 * self.llf / max(phi_ref, 1e-9) + 2 * self.k)


def fit_poisson_fe(
    y: np.ndarray, groups: np.ndarray, xreg: np.ndarray, max_iter: int = 100, tol: float = 1e-10
) -> GLMResult:
    """Poisson regression log mu = alpha_group + xreg @ beta."""
    y = np.asarray(y, dtype=float)
    xreg = np.asarray(xreg, dtype=float).reshape(len(y), -1)
    g_codes, g_idx = np.unique(groups, return_inverse=True)
    # drop groups with zero total count (their fixed effect would be -inf)
    tot = np.bincount(g_idx, weights=y)
    keep = tot[g_idx] > 0
    y, xreg, g_idx = y[keep], xreg[keep], g_idx[keep]
    _, g_idx = np.unique(g_idx, return_inverse=True)
    n_g = int(np.max(g_idx)) + 1
    fe = np.zeros((len(y), n_g))
    fe[np.arange(len(y)), g_idx] = 1.0
    x = np.hstack([fe, xreg])
    beta = np.zeros(x.shape[1])
    beta[:n_g] = np.log(np.bincount(g_idx, weights=y) / np.bincount(g_idx))
    for _ in range(max_iter):
        eta = x @ beta
        mu = np.exp(eta)
        z = eta + (y - mu) / mu
        w = mu
        xtw = x.T * w
        new = np.linalg.solve(xtw @ x + 1e-12 * np.eye(x.shape[1]), xtw @ z)
        if np.max(np.abs(new - beta)) < tol:
            beta = new
            break
        beta = new
    mu = np.exp(x @ beta)
    p = x.shape[1]
    phi = float(np.sum((y - mu) ** 2 / mu) / max(len(y) - p, 1))
    cov = np.linalg.inv((x.T * mu) @ x)
    se = np.sqrt(np.maximum(phi, 1.0) * np.diag(cov))
    with np.errstate(divide="ignore", invalid="ignore"):
        llf = float(np.sum(y * np.log(np.where(y > 0, mu, 1.0)) - mu - _lgamma1(y)))
    return GLMResult(coef=beta[n_g:], se=se[n_g:], phi=phi, llf=llf, n=len(y), k=p, mu=mu)


def _lgamma1(y: np.ndarray) -> np.ndarray:
    from scipy.special import gammaln

    return np.asarray(gammaln(y + 1))
