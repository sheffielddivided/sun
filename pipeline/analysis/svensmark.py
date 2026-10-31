"""Svensmark-hypotesen: korrelerer kosmisk stråling (proxy: −Φ) med skydekke fra ISCCP-H (1984–2016)?

Hypotesen predikerer at mer kosmisk stråling (lav Φ) gir mer lavt skydekke, dvs. positiv korrelasjon mellom CR-proxyen (−Φ) og lavt skydekke.
Skydekke: månedlige anomalier (avvik fra månedsklimatologi), årsmiddel for hele år. Hovedanalysen trendfjerner (lineært) siden ISCCP har kjente
instrumentdrifter. 6 serier (globalt/tropene/midlere bredder × totalt/lavt) × 4 forsinkelser (skyer forsinket 0…2 år, og −1) = 24 tester.
"""

from __future__ import annotations

import numpy as np

from ..core import DATA_DIR, read_json
from . import stats as S
from .data import _arr, align, annual_from_monthly, yearly_ssn
from .solar_earth import N_SURR, _corr_dict, _round

SERIES = [("global", "low"), ("global", "total"), ("tropics", "low"), ("tropics", "total"), ("midlat", "low"), ("midlat", "total")]
LAGS = [-1, 0, 1, 2]


def annual_anomaly(t: np.ndarray, v: np.ndarray) -> dict[int, float]:
    year = np.floor(t + 1e-9).astype(int)
    month = np.round((t - year) * 12 + 0.5).astype(int)
    clim = {m: np.nanmean(v[month == m]) for m in range(1, 13)}
    anom = np.array([x - clim[m] if np.isfinite(x) else np.nan for x, m in zip(v, month)])
    return annual_from_monthly(t, anom)


def analyse_svensmark(outdir=DATA_DIR) -> dict:
    rng = S.rng_for("svensmark")
    c = read_json("cloud_isccp_monthly.json", outdir)
    t = _arr(c["t"])
    phi_d = read_json("cosmic_phi_monthly.json", outdir)
    phi = annual_from_monthly(_arr(phi_d["t"]), _arr(phi_d["phi"]))
    cr = {y: -v for y, v in phi.items()}  # proxy for intensitet av kosmisk stråling
    ssn = yearly_ssn(outdir)
    pvals: list[float] = []
    res = {"n_surrogates": N_SURR, "lags_tested": LAGS, "series": {}}
    detrend = lambda a: S.detrend_linear(a)  # noqa: E731
    for band, kind in SERIES:
        ann = annual_anomaly(t, _arr(c[band][kind]))
        yrs, (x, y) = align(cr, ann)
        scan = S.lag_scan(x, detrend(y), LAGS, rng, N_SURR)
        scan["period"] = [int(yrs[0]), int(yrs[-1])]
        res["series"][f"{band}_{kind}"] = scan
        pvals += [row["p_surrogate"] for row in scan["lags"]]
    adj = S.holm(pvals)
    k = 0
    for key in res["series"]:
        for row in res["series"][key]["lags"]:
            row["p_holm_all"] = adj[k]
            k += 1
    res["n_tests"] = len(pvals)
    res["min_p_holm_all"] = float(min(adj))
    # Hovedserie: globalt lavt skydekke
    ann = annual_anomaly(t, _arr(c["global"]["low"]))
    yrs, (x, y) = align(cr, ann)
    raw = S.correlate(x, y, rng, N_SURR)
    det = S.correlate(x, detrend(y), rng, N_SURR)
    reg = S.regression_slope(x, detrend(y), det.neff)
    phi_rng = float(np.percentile(-x, 95) - np.percentile(-x, 5))
    res["main"] = {
        "period": [int(yrs[0]), int(yrs[-1])],
        "n_years": len(yrs),
        "raw": _corr_dict(raw),
        "detrended": _corr_dict(det),
        "slope_pct_per_100mv": 100 * reg["slope"],
        "slope_ci": [100 * reg["ci_lo"], 100 * reg["ci_hi"]],
        "cr_range_mv_p5_p95": phi_rng,
        "implied_cycle_change_pct": reg["slope"] * phi_rng,
        "implied_cycle_ci": [reg["ci_lo"] * phi_rng, reg["ci_hi"] * phi_rng],
        "linear_trend_pct_per_decade": 10 * S.ols_trend(yrs.astype(float), y)["slope"],
        "linear_trend_ci": [10 * S.ols_trend(yrs.astype(float), y)["ci_lo"], 10 * S.ols_trend(yrs.astype(float), y)["ci_hi"]],
    }
    # Delperioder (der kjente funn om «sammenbrudd» etter ca. 2000 gjelder)
    sub = {}
    for name, (a, b) in {"early": (1984, 2000), "late": (2001, 2016)}.items():
        yy, (xs, ys) = align(cr, ann, y0=a, y1=b)
        sub[name] = {"period": [int(yy[0]), int(yy[-1])], **_corr_dict(S.correlate(xs, detrend(ys), rng, N_SURR))}
    res["subperiods"] = sub
    res["n_tests"] += 2 + 2
    # Samme mot solflekktall (positiv: aktiv sol → mer/mindre skyer?) for sammenligning
    yy, (xs, ys) = align(ssn, ann)
    res["vs_ssn_global_low"] = _corr_dict(S.correlate(xs, detrend(ys), rng, N_SURR))
    # Figurdata
    res["series_data"] = {"year": [int(v) for v in yrs], "cr_proxy_neg_phi": (x - x.mean()).tolist(), "global_low_anom_detrended": detrend(y).tolist(), "global_low_anom": y.tolist()}
    # Minste påviselige korrelasjon ved effektive frihetsgrader (80 % styrke, α = 0,05, tosidig) – tilnærmet
    from scipy import stats as sps

    neff = max(det.neff, 5.0)
    z = (sps.norm.ppf(0.975) + sps.norm.ppf(0.8)) / np.sqrt(neff - 3)
    res["min_detectable_r"] = float(np.tanh(z))
    return _round(res, 4)
