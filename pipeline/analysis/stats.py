"""Statistiske verktøy: autokorrelasjonskorrigert korrelasjon, surrogattester, lag-skanning med multippel-testkorreksjon.

Metoder
-------
* Effektive frihetsgrader (Bretherton et al. 1999): N_eff = N (1 − r1x·r1y) / (1 + r1x·r1y), r1 = lag-1-autokorrelasjon.
* Konfidensintervall for Pearson-r via Fisher-z med N_eff − 3 frihetsgrader.
* Fase-surrogater (Theiler et al. 1992; Schreiber & Schmitz 2000): FFT-fasene randomiseres, amplitudespekteret bevares,
  slik at autokorrelasjonen (inkl. solsyklusen) bevares men enhver kobling til den andre serien brytes.
* Lag-skanning: per-lag p-verdi fra surrogatfordelingen, Holm-justering (Holm 1979) og en familievis p-verdi
  fra fordelingen av maksimum |r| over alle lag (kontrollerer FWER, tar hensyn til at lagene er korrelert).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import stats as sps


def rng_for(name: str, seed: int = 20260101) -> np.random.Generator:
    """Deterministisk generator per analyse (reproduserbare resultater når dataene er like)."""
    h = int.from_bytes(name.encode("utf-8")[:16].ljust(16, b"\0"), "little") % (2**32)
    return np.random.default_rng([seed, h])


def lag1_autocorr(x: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    x = x - x.mean()
    d = float((x * x).sum())
    if d == 0:
        return 0.0
    return float((x[:-1] * x[1:]).sum() / d)


def pearson(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    xc, yc = x - x.mean(), y - y.mean()
    den = np.sqrt((xc * xc).sum() * (yc * yc).sum())
    return float((xc * yc).sum() / den) if den > 0 else 0.0


def effective_n(x: np.ndarray, y: np.ndarray) -> float:
    """Bretherton-estimat. Begrenses til [3, N]: negativ produkt av autokorrelasjoner gir ikke flere enn N frihetsgrader."""
    n = len(x)
    rx, ry = lag1_autocorr(x), lag1_autocorr(y)
    prod = rx * ry
    neff = n * (1 - prod) / (1 + prod) if prod > -0.999 else n
    return float(min(max(neff, 3.0), n))


def fisher_ci(r: float, neff: float, level: float = 0.95) -> tuple[float, float]:
    if neff <= 4 or abs(r) >= 1:
        return (float("nan"), float("nan"))
    z = np.arctanh(r)
    se = 1.0 / np.sqrt(neff - 3)
    q = sps.norm.ppf(0.5 + level / 2)
    return (float(np.tanh(z - q * se)), float(np.tanh(z + q * se)))


def neff_pvalue(r: float, neff: float) -> float:
    """To-sidig p-verdi for r mot null, med N_eff i stedet for N (t-test)."""
    if neff <= 2:
        return 1.0
    r = float(np.clip(r, -0.999999, 0.999999))
    t = r * np.sqrt((neff - 2) / (1 - r * r))
    return float(2 * sps.t.sf(abs(t), neff - 2))


def phase_surrogates(x: np.ndarray, n: int, rng: np.random.Generator) -> np.ndarray:
    """n fase-randomiserte surrogater av x (form: n × len(x)). Middelverdi og amplitudespekter bevares."""
    x = np.asarray(x, dtype=float)
    N = len(x)
    mu = x.mean()
    F = np.fft.rfft(x - mu)
    amp = np.abs(F)
    nf = len(F)
    ph = rng.uniform(0, 2 * np.pi, size=(n, nf))
    ph[:, 0] = 0.0
    if N % 2 == 0:
        ph[:, -1] = 0.0  # Nyquist-komponenten må være reell
    S = amp[None, :] * np.exp(1j * ph)
    return np.fft.irfft(S, n=N, axis=1) + mu


def corr_matrix_rows(S: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Pearson-r mellom hver rad i S og y."""
    Sc = S - S.mean(axis=1, keepdims=True)
    yc = y - y.mean()
    num = Sc @ yc
    den = np.sqrt((Sc * Sc).sum(axis=1) * (yc * yc).sum())
    with np.errstate(invalid="ignore", divide="ignore"):
        out = np.where(den > 0, num / den, 0.0)
    return out


@dataclass
class CorrResult:
    r: float
    n: int
    neff: float
    ci: tuple[float, float]
    p_neff: float
    p_surrogate: float

    def as_dict(self) -> dict:
        return {
            "r": self.r,
            "n": self.n,
            "neff": self.neff,
            "ci_lo": self.ci[0],
            "ci_hi": self.ci[1],
            "p_neff": self.p_neff,
            "p_surrogate": self.p_surrogate,
        }


def correlate(x: np.ndarray, y: np.ndarray, rng: np.random.Generator, n_surr: int = 2000) -> CorrResult:
    """Én korrelasjon med N_eff-konfidensintervall og surrogat-p-verdi (to-sidig)."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    r = pearson(x, y)
    neff = effective_n(x, y)
    S = phase_surrogates(x, n_surr, rng)
    rs = corr_matrix_rows(S, y)
    p = (1 + int((np.abs(rs) >= abs(r) - 1e-12).sum())) / (n_surr + 1)
    return CorrResult(r, len(x), neff, fisher_ci(r, neff), neff_pvalue(r, neff), p)


def holm(pvals: list[float]) -> list[float]:
    m = len(pvals)
    order = np.argsort(pvals)
    adj = np.empty(m)
    running = 0.0
    for rank, idx in enumerate(order):
        val = (m - rank) * pvals[idx]
        running = max(running, val)
        adj[idx] = min(1.0, running)
    return adj.tolist()


def lag_scan(x: np.ndarray, y: np.ndarray, lags: list[int], rng: np.random.Generator, n_surr: int = 2000) -> dict:
    """Skann lag L: korrelasjon mellom x[t] og y[t+L] (positiv L: x leder y). x og y må være like lange, uten NaN.

    Surrogatene lages for hele x én gang; samme utsnitt brukes som for observasjonene. p_family er andelen
    surrogatsett der største |r| over alle lag ≥ observert største |r| (familievis feilrate, FWER).
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    assert len(x) == len(y)
    N = len(x)
    S = phase_surrogates(x, n_surr, rng)
    rows, rs_cols, r_obs = [], [], []
    for L in lags:
        if L >= 0:
            xs, ys, Ss = x[: N - L], y[L:], S[:, : N - L]
        else:
            xs, ys, Ss = x[-L:], y[: N + L], S[:, -L:]
        r = pearson(xs, ys)
        neff = effective_n(xs, ys)
        rs = corr_matrix_rows(Ss, ys)
        p_s = (1 + int((np.abs(rs) >= abs(r) - 1e-12).sum())) / (n_surr + 1)
        lo, hi = fisher_ci(r, neff)
        rows.append({"lag": L, "r": r, "n": len(xs), "neff": neff, "ci_lo": lo, "ci_hi": hi, "p_neff": neff_pvalue(r, neff), "p_surrogate": p_s})
        rs_cols.append(rs)
        r_obs.append(r)
    M = np.abs(np.vstack(rs_cols)).max(axis=0)  # maks |r| per surrogat over alle lag
    best = int(np.argmax(np.abs(r_obs)))
    p_family = (1 + int((M >= abs(r_obs[best]) - 1e-12).sum())) / (n_surr + 1)
    holm_adj = holm([row["p_surrogate"] for row in rows])
    for row, h in zip(rows, holm_adj):
        row["p_holm"] = h
    return {
        "lags": rows,
        "n_tests": len(lags),
        "n_surrogates": n_surr,
        "best_lag": rows[best]["lag"],
        "best_r": rows[best]["r"],
        "p_family": p_family,
        "min_p_holm": min(row["p_holm"] for row in rows),
    }


def ols_trend(t: np.ndarray, y: np.ndarray) -> dict:
    """Lineær trend med AR(1)-justert standardfeil (residualenes lag-1-autokorrelasjon). Returnerer slope per tidsenhet."""
    t = np.asarray(t, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(t)
    A = np.vstack([t, np.ones(n)]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    res = y - A @ coef
    s2 = float((res**2).sum() / (n - 2))
    sxx = float(((t - t.mean()) ** 2).sum())
    se = np.sqrt(s2 / sxx)
    r1 = max(lag1_autocorr(res), 0.0)
    neff = max(n * (1 - r1) / (1 + r1), 3.0)
    se_adj = se * np.sqrt(n / neff) if neff < n else se
    dof = max(neff - 2, 1.0)
    q = sps.t.ppf(0.975, dof)
    return {"slope": float(coef[0]), "intercept": float(coef[1]), "se_adj": float(se_adj), "ci_lo": float(coef[0] - q * se_adj), "ci_hi": float(coef[0] + q * se_adj), "n": n, "neff": float(neff)}


def detrend_linear(y: np.ndarray) -> np.ndarray:
    t = np.arange(len(y), dtype=float)
    A = np.vstack([t, np.ones(len(y))]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    return y - A @ coef


def regression_slope(x: np.ndarray, y: np.ndarray, neff: float) -> dict:
    """Regresjon y = a + b x med konfidensintervall der N_eff erstatter N."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)
    xc = x - x.mean()
    b = float((xc * (y - y.mean())).sum() / (xc**2).sum())
    a = float(y.mean() - b * x.mean())
    res = y - (a + b * x)
    s2 = float((res**2).sum() / (n - 2))
    se = np.sqrt(s2 / (xc**2).sum()) * np.sqrt(n / max(neff, 3.0))
    q = sps.t.ppf(0.975, max(neff - 2, 1.0))
    return {"slope": b, "intercept": a, "ci_lo": float(b - q * se), "ci_hi": float(b + q * se)}
