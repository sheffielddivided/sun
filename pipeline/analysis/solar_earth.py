"""Analyser for «Sol og jord»: TSI, temperatur, kosmisk stråling, geomagnetisk aktivitet, regionale mønstre.

Alle analyser bruker de genererte JSON-seriene i public/data og returnerer en dict som skrives til analysis_<navn>.json.
Hver analyse oppgir hvor mange tester som ble kjørt (`n_tests`). Tall i teksten på nettsiden hentes herfra.
"""

from __future__ import annotations

import numpy as np

from ..core import DATA_DIR, read_json
from . import stats as S
from .cycles import phase_of
from .data import _arr, align, annual_from_monthly, monthly_ssn, yearly_ssn

N_SURR = 2000
ALBEDO = 0.30  # antatt jordalbedo for omregning TSI → strålingspådriv (ΔF = ΔTSI · (1 − A) / 4)


def _round(o, nd=4):
    if isinstance(o, dict):
        return {k: _round(v, nd) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_round(v, nd) for v in o]
    if isinstance(o, (float, np.floating)):
        return None if not np.isfinite(o) else round(float(o), nd)
    if isinstance(o, np.integer):
        return int(o)
    return o


def _corr_dict(res: S.CorrResult) -> dict:
    return _round(res.as_dict())


# ---------------------------------------------------------------------------------------------------
def analyse_tsi(cycles: list[dict], outdir=DATA_DIR) -> dict:
    rng = S.rng_for("tsi")
    tsi = read_json("tsi_yearly.json", outdir)
    nnl = {int(y): v for y, v in zip(tsi["year"], _arr(tsi["tsi"])) if np.isfinite(v)}
    ssn_y = yearly_ssn(outdir)

    # Amplitude per syklus (maks − min av årlige NNL-verdier innenfor syklusen)
    per_cycle = []
    for c in cycles:
        if not c["complete"] or c["n"] < 12:
            continue
        ys = [y for y in range(int(c["start_t"]), int(c["end_t"]) + 1) if y in nnl]
        if len(ys) < 8:
            continue
        v = [nnl[y] for y in ys]
        per_cycle.append({"cycle": c["n"], "tsi_max": max(v), "tsi_min": min(v), "range_wm2": max(v) - min(v)})
    last5 = [c["range_wm2"] for c in per_cycle if c["cycle"] >= 20]
    mean_range = float(np.mean(last5))
    # Målt (TSIS-1) økning siden minimum
    ts = read_json("tsi_tsis_monthly.json", outdir)
    tt, tv = _arr(ts["t"]), _arr(ts["tsi"])
    # 13-måneders glidende middel fjerner månedsstøy og rotasjonsmodulasjon før minimum/maksimum velges
    k = 13
    sm13 = np.full(len(tv), np.nan)
    for i in range(k // 2, len(tv) - k // 2):
        sm13[i] = tv[i - k // 2 : i + k // 2 + 1].mean()
    i_min = int(np.nanargmin(np.where(tt < 2023, sm13, np.nan)))
    i_max = int(np.nanargmax(sm13))
    tsis_rise = float(sm13[i_max] - sm13[i_min])
    mean_tsi = float(np.nanmean(tv))

    # Korrelasjon NNL–SSN (årlig). Merk: NNL er en modell som bruker solflekker/fakkelindekser som proxy → ikke uavhengig.
    yrs, (x, y) = align(ssn_y, nnl, y0=1749, y1=2025)
    corr = S.correlate(x, y, rng, N_SURR)

    # Minimumsnivå: NNL ved begynnelsen av syklus 21–25
    minima = []
    for c in cycles:
        if c["n"] >= 21:
            y0 = int(round(c["start_t"]))
            if y0 in nnl:
                minima.append({"cycle": c["n"], "year": y0, "tsi": nnl[y0]})
    return _round(
        {
            "n_tests": 1,
            "n_surrogates": N_SURR,
            "per_cycle": per_cycle,
            "mean_range_cycles_20_24": mean_range,
            "mean_range_pct": 100 * mean_range / float(np.mean(list(nnl.values()))),
            "tsis_rise_wm2": tsis_rise,
            "tsis_rise_pct": 100 * tsis_rise / mean_tsi,
            "tsis_min_t": float(tt[i_min]),
            "tsis_max_t": float(tt[i_max]),
            "forcing_equiv_wm2": mean_range * (1 - ALBEDO) / 4,
            "albedo_assumed": ALBEDO,
            "corr_nnl_ssn": _corr_dict(corr),
            "corr_period": [int(yrs[0]), int(yrs[-1])],
            "cycle_minima_tsi": minima,
            "ar6_anthropogenic_erf_wm2": 2.72,
        },
        3,
    )


# ---------------------------------------------------------------------------------------------------
def _poly_detrend(y: np.ndarray, deg: int = 2) -> np.ndarray:
    x = np.linspace(-1, 1, len(y))
    return y - np.polyval(np.polyfit(x, y, deg), x)


def analyse_temperature(outdir=DATA_DIR) -> dict:
    rng = S.rng_for("temperature")
    ssn_y = yearly_ssn(outdir)
    ta = read_json("temp_annual.json", outdir)
    giss = {int(y): v for y, v in zip(ta["year"], _arr(ta["gistemp"])) if np.isfinite(v)}
    had = {int(y): v for y, v in zip(ta["year"], _arr(ta["hadcrut5"])) if np.isfinite(v)}
    tsi = read_json("tsi_yearly.json", outdir)
    nnl = {int(y): v for y, v in zip(tsi["year"], _arr(tsi["tsi"])) if np.isfinite(v)}
    lags = list(range(0, 11))
    out = {"n_surrogates": N_SURR, "lags_tested": lags, "detrend": "andregrads polynom (fjerner jevn langtidstrend/akselerasjon)"}
    n_tests = 0
    for key, series, y0 in (("gistemp", giss, 1880), ("hadcrut5", had, 1850)):
        yrs, (x, y) = align(ssn_y, series, y0=y0)
        scan = S.lag_scan(x, _poly_detrend(y), lags, rng, N_SURR)
        scan["period"] = [int(yrs[0]), int(yrs[-1])]
        out[f"scan_{key}"] = scan
        n_tests += len(lags)
    # Delperioder (lag 0), GISTEMP
    sub = {}
    for name, (a, b) in {"pre1980": (1880, 1979), "post1980": (1980, 2025)}.items():
        yrs, (x, y) = align(ssn_y, giss, y0=a, y1=b)
        raw = S.correlate(x, y, rng, N_SURR)
        det = S.correlate(x, _poly_detrend(y, 1), rng, N_SURR)
        sub[name] = {"period": [int(yrs[0]), int(yrs[-1])], "raw": _corr_dict(raw), "detrended_linear": _corr_dict(det)}
        n_tests += 2
    out["subperiods"] = sub
    # Trender 1980–2025
    t0, t1 = 1980, 2025
    yrs, (x, yg, yh) = align(ssn_y, giss, had, y0=t0, y1=t1)
    trend_t = S.ols_trend(yrs.astype(float), yg)
    trend_h = S.ols_trend(yrs.astype(float), yh)
    trend_s = S.ols_trend(yrs.astype(float), x)
    ty = [y for y in range(t0, t1 + 1) if y in nnl]
    trend_tsi = S.ols_trend(np.array(ty, float), np.array([nnl[y] for y in ty]))
    nyr = t1 - t0
    # Hva ville fallende solaktivitet gi hvis pre-1980-koeffisienten var fullt kausal?
    yrs_p, (xp, yp) = align(ssn_y, giss, y0=1880, y1=1979)
    reg = S.regression_slope(xp, _poly_detrend(yp, 2), S.effective_n(xp, yp))
    implied = reg["slope"] * trend_s["slope"] * nyr
    out["trend_1980_2025"] = {
        "period": [t0, t1],
        "gistemp_c_per_decade": 10 * trend_t["slope"],
        "gistemp_ci": [10 * trend_t["ci_lo"], 10 * trend_t["ci_hi"]],
        "hadcrut5_c_per_decade": 10 * trend_h["slope"],
        "hadcrut5_ci": [10 * trend_h["ci_lo"], 10 * trend_h["ci_hi"]],
        "gistemp_total_change_c": trend_t["slope"] * nyr,
        "ssn_per_decade": 10 * trend_s["slope"],
        "ssn_ci": [10 * trend_s["ci_lo"], 10 * trend_s["ci_hi"]],
        "ssn_total_change": trend_s["slope"] * nyr,
        "tsi_wm2_per_decade": 10 * trend_tsi["slope"],
        "tsi_ci": [10 * trend_tsi["ci_lo"], 10 * trend_tsi["ci_hi"]],
        "regression_pre1980_c_per_100ssn": 100 * reg["slope"],
        "regression_ci": [100 * reg["ci_lo"], 100 * reg["ci_hi"]],
        "implied_solar_change_c": implied,
    }
    # Figurdata: 11-årig glidende middel av SSN og temperaturer
    all_years = sorted(set(giss) & set(ssn_y))
    sm = {}
    for y in all_years:
        win = [ssn_y[k] for k in range(y - 5, y + 6) if k in ssn_y]
        if len(win) == 11:
            sm[y] = float(np.mean(win))
    out["series"] = {"year": all_years, "ssn_smooth11": [sm.get(y) for y in all_years]}
    out["n_tests"] = n_tests
    return _round(out, 4)


# ---------------------------------------------------------------------------------------------------
def analyse_cosmic(outdir=DATA_DIR) -> dict:
    rng = S.rng_for("cosmic")
    ssn_y = yearly_ssn(outdir)
    cp = read_json("cosmic_phi_monthly.json", outdir)
    phi = annual_from_monthly(_arr(cp["t"]), _arr(cp["phi"]))
    ta = read_json("temp_annual.json", outdir)
    giss = {int(y): v for y, v in zip(ta["year"], _arr(ta["gistemp"])) if np.isfinite(v)}
    lags = list(range(-2, 4))
    yrs, (x, y) = align(ssn_y, phi)
    scan = S.lag_scan(x, y, lags, rng, N_SURR)
    scan["period"] = [int(yrs[0]), int(yrs[-1])]
    # Φ mot temperatur (rå og detrendet) – illustrerer hvorfor korrelasjoner er vanskelige å tolke
    yrs2, (p2, g2) = align(phi, giss)
    raw = S.correlate(p2, g2, rng, N_SURR)
    det = S.correlate(p2, _poly_detrend(g2, 2), rng, N_SURR)
    # Trender
    tr_phi = S.ols_trend(yrs2.astype(float)[yrs2 >= 1980], p2[yrs2 >= 1980])
    return _round(
        {
            "n_tests": len(lags) + 2,
            "n_surrogates": N_SURR,
            "lags_tested": lags,
            "scan_phi_ssn": scan,
            "phi_vs_temp_raw": _corr_dict(raw),
            "phi_vs_temp_detrended": _corr_dict(det),
            "phi_temp_period": [int(yrs2[0]), int(yrs2[-1])],
            "phi_trend_1980_mv_per_decade": 10 * tr_phi["slope"],
            "phi_trend_1980_ci": [10 * tr_phi["ci_lo"], 10 * tr_phi["ci_hi"]],
            "phi_range": [float(np.min(y)), float(np.max(y))],
        },
        4,
    )


# ---------------------------------------------------------------------------------------------------
def analyse_geomag(cycles: list[dict], outdir=DATA_DIR) -> dict:
    rng = S.rng_for("geomag")
    g = read_json("geomag_monthly.json", outdir)
    t = _arr(g["t"])
    ap, storm, severe, days = _arr(g["ap_mean"]), _arr(g["storm_days"]), _arr(g["severe_days"]), _arr(g["days"])
    full = days >= 27
    ap_m = np.where(full, ap, np.nan)
    storm_m = np.where(full, storm, np.nan)
    sev_m = np.where(full, severe, np.nan)
    ap_y = annual_from_monthly(t, ap_m)
    # årlige summer av stormdøgn (kun år med 12 komplette måneder)
    years = np.floor(t + 1e-9).astype(int)
    storm_y, sev_y = {}, {}
    for y in np.unique(years):
        m = (years == y) & np.isfinite(storm_m)
        if m.sum() == 12:
            storm_y[int(y)] = float(storm_m[m].sum())
            sev_y[int(y)] = float(sev_m[m].sum())
    ssn_y = yearly_ssn(outdir)
    lags = list(range(0, 5))
    res = {"n_surrogates": N_SURR, "lags_tested": lags}
    for key, ser in (("storm_days", storm_y), ("ap", ap_y)):
        yrs, (x, y) = align(ssn_y, ser)
        sc = S.lag_scan(x, y, lags, rng, N_SURR)
        sc["period"] = [int(yrs[0]), int(yrs[-1])]
        res[f"scan_{key}"] = sc
    # Faseprofil: gjennomsnitt per syklusfase i fullførte sykluser fra og med syklus 17 (1933) – GFZ starter 1932
    sm = monthly_ssn(outdir)
    ph = phase_of(t, cycles)
    ph_ssn = phase_of(sm["t"], cycles)
    first_full = [c for c in cycles if c["complete"] and c["start_t"] >= 1932.9]
    nb = 10
    prof = {"ap": [], "storm_days": [], "ssn": [], "ap_sd": [], "storm_sd": []}
    cyc_mean_ap = {b: [] for b in range(nb)}
    cyc_mean_st = {b: [] for b in range(nb)}
    for b in range(nb):
        for c in first_full:
            m = (t >= c["start_t"]) & (t < c["end_t"]) & (ph >= b / nb) & (ph < (b + 1) / nb) & full
            if m.sum() > 0:
                cyc_mean_ap[b].append(float(ap[m].mean()))
                cyc_mean_st[b].append(float(storm[m].mean()))
        ms = (ph_ssn >= b / nb) & (ph_ssn < (b + 1) / nb) & (sm["t"] >= first_full[0]["start_t"]) & np.isfinite(sm["smoothed"])
        prof["ssn"].append(float(sm["smoothed"][ms].mean()))
    for b in range(nb):
        prof["ap"].append(float(np.mean(cyc_mean_ap[b])))
        prof["ap_sd"].append(float(np.std(cyc_mean_ap[b], ddof=1)))
        prof["storm_days"].append(float(np.mean(cyc_mean_st[b])))
        prof["storm_sd"].append(float(np.std(cyc_mean_st[b], ddof=1)))
    peak_bin = int(np.argmax(prof["storm_days"]))
    res["phase_profile"] = {"bins": nb, "n_cycles": len(first_full), "cycles": [c["n"] for c in first_full], **prof, "storm_peak_bin": peak_bin}
    # Scatter + totalt
    yrs, (xs, st) = align(ssn_y, storm_y)
    res["scatter"] = {"year": yrs.tolist(), "ssn": xs.tolist(), "storm_days": st.tolist()}
    res["annual_storm_days_mean"] = float(np.mean(list(storm_y.values())))
    res["n_tests"] = 2 * len(lags)
    return _round(res, 4)


# ---------------------------------------------------------------------------------------------------
def _winter_mean(t: np.ndarray, v: np.ndarray) -> dict[int, float]:
    """DJF-gjennomsnitt, tilordnet året til januar/februar. Krever alle tre månedene."""
    year = np.floor(t + 1e-9).astype(int)
    month = np.round((t - year) * 12 + 0.5).astype(int)
    d = {(int(y), int(m)): x for y, m, x in zip(year, month, v) if np.isfinite(x)}
    out = {}
    for y in sorted({k[0] for k in d}):
        keys = [(y - 1, 12), (y, 1), (y, 2)]
        if all(k in d for k in keys):
            out[y] = float(np.mean([d[k] for k in keys]))
    return out


def analyse_regional(outdir=DATA_DIR) -> dict:
    rng = S.rng_for("regional")
    ssn_y = yearly_ssn(outdir)
    nao = read_json("nao_monthly.json", outdir)
    oni = read_json("oni_monthly.json", outdir)
    nao_w = _winter_mean(_arr(nao["t"]), _arr(nao["nao"]))
    oni_w = _winter_mean(_arr(oni["t"]), _arr(oni["oni"]))
    lags = list(range(0, 6))
    res = {"n_surrogates": N_SURR, "lags_tested": lags}
    for key, ser in (("nao_djf", nao_w), ("oni_djf", oni_w)):
        yrs, (x, y) = align(ssn_y, ser)
        sc = S.lag_scan(x, y, lags, rng, N_SURR)
        sc["period"] = [int(yrs[0]), int(yrs[-1])]
        res[f"scan_{key}"] = sc
    # Figurdata
    yrs, (x, y) = align(ssn_y, nao_w)
    res["nao_series"] = {"year": yrs.tolist(), "ssn": x.tolist(), "nao_djf": y.tolist()}
    res["n_tests"] = 2 * len(lags)
    res["n_cycles_covered"] = round((yrs[-1] - yrs[0]) / 11.0, 1)
    return _round(res, 4)
