"""Vulkanutbrudd og solaktivitet: faser i solsyklusen, høy/lav aktivitet og superposed epoch-analyse.

Nullhypotese: utbruddenes tidspunkter er uavhengige av solsyklusen. Nullfordelingen lages ved å skifte hele utbruddsrekken
sirkulært (modulo vindulengde) med et tilfeldig forskyvning. Det bevarer utbruddenes antall, innbyrdes avstander (klynging),
og eventuelle langsiktige endringer i registrering (rapporteringsskjevhet), men bryter koblingen til solsyklusen.
Skiftene er jevnt fordelt, så fasene i solsyklusen sampler alle mulige forskyvninger.

Perioden avgrenses til fullførte sykluser (1755–2019,96 ved syklus 25-start). Primærscenarioene er valgt på forhånd:
  A: VEI ≥ 4, 1850–2019  (registreringen er rimelig stabil per 50 år etter ca. 1850, se `reporting`)
  B: VEI ≥ 5, 1755–2019  (store utbrudd rapporteres i større grad også tidligere)
Øvrige scenarier er følsomhetsanalyser. Holm-justering gjøres over de 6 primærtestene.
"""

from __future__ import annotations

import numpy as np

from ..core import DATA_DIR, read_json
from . import stats as S
from .cycles import phase_of
from .data import _arr, monthly_ssn, yearly_ssn
from .solar_earth import _round

N_SHIFT = 10000
NB_PHASE = 4
LAGS = list(range(-5, 6))

SCENARIOS = [
    # id, label, vei_min, y0, y1, only_precise, primary
    ("A", "VEI ≥ 4, 1850–2019", 4, 1850.0, None, False, True),
    ("B", "VEI ≥ 5, 1755–2019", 5, None, None, False, True),
    ("C", "VEI ≥ 4, 1755–2019", 4, None, None, False, False),
    ("D", "VEI ≥ 4, 1900–2019", 4, 1900.0, None, False, False),
    ("E", "VEI ≥ 5, 1850–2019", 5, 1850.0, None, False, False),
    ("F", "VEI ≥ 4, 1850–2019, kun presise startdatoer", 4, 1850.0, None, True, False),
]


def _sea_composite(ssn_anom: dict[int, float], event_years: np.ndarray) -> np.ndarray:
    comp = np.full(len(LAGS), np.nan)
    for j, k in enumerate(LAGS):
        vals = [ssn_anom[int(y) + k] for y in event_years if int(y) + k in ssn_anom]
        if vals:
            comp[j] = np.mean(vals)
    return comp


def run_scenario(sid, label, vei_min, y0, y1, only_precise, primary, ev: dict, cycles, sm, ssn_y, rng) -> dict:
    cyc_start = cycles[0]["start_t"]
    end = [c for c in cycles if not c["complete"]][0]["start_t"]  # start av syklus 25 = slutt på siste fullførte
    y0 = cyc_start if y0 is None else max(y0, cyc_start)
    y1 = end if y1 is None else min(y1, end)
    L = y1 - y0
    sel = (ev["vei"] >= vei_min) & (ev["t"] >= y0) & (ev["t"] < y1) & ev["confirmed"]
    if only_precise:
        sel &= ev["precise"]
    t_ev = ev["t"][sel]
    n = len(t_ev)

    # månedsgrid i vinduet for forventede andeler
    grid = np.arange(y0, y1, 1 / 12) + 1 / 24
    ph_grid = phase_of(grid, cycles)
    sm_grid = np.interp(grid, sm["t"][np.isfinite(sm["smoothed"])], sm["smoothed"][np.isfinite(sm["smoothed"])])
    median = np.median(sm_grid)
    high_grid = sm_grid > median
    f_high = float(high_grid.mean())
    exp_frac = np.array([np.mean((ph_grid >= b / NB_PHASE) & (ph_grid < (b + 1) / NB_PHASE)) for b in range(NB_PHASE)])
    exp_frac = exp_frac / exp_frac.sum()

    def phase_counts(times):
        ph = phase_of(times, cycles)
        return np.array([np.sum((ph >= b / NB_PHASE) & (ph < (b + 1) / NB_PHASE)) for b in range(NB_PHASE)])

    def high_count(times):
        s = np.interp(times, sm["t"][np.isfinite(sm["smoothed"])], sm["smoothed"][np.isfinite(sm["smoothed"])])
        return int((s > median).sum())

    # SEA: standardiserte årlige SSN-anomalier (avvik fra middel i vinduet)
    yrs_w = [y for y in ssn_y if y0 <= y < y1]
    mu, sd = np.mean([ssn_y[y] for y in yrs_w]), np.std([ssn_y[y] for y in yrs_w])
    anom = {y: (v - mu) / sd for y, v in ssn_y.items()}

    exp_counts = exp_frac * n
    obs_counts = phase_counts(t_ev)
    chi_obs = float((((obs_counts - exp_counts) ** 2) / exp_counts).sum())
    high_obs = high_count(t_ev)
    comp_obs = _sea_composite(anom, np.floor(t_ev))

    shifts = rng.uniform(0, L, size=N_SHIFT)
    chi_null = np.empty(N_SHIFT)
    high_null = np.empty(N_SHIFT)
    comp_null = np.empty((N_SHIFT, len(LAGS)))
    for i, d in enumerate(shifts):
        tt = y0 + np.mod(t_ev - y0 + d, L)
        c = phase_counts(tt)
        chi_null[i] = (((c - exp_counts) ** 2) / exp_counts).sum()
        high_null[i] = high_count(tt)
        comp_null[i] = _sea_composite(anom, np.floor(tt))
    p_phase = (1 + int((chi_null >= chi_obs - 1e-12).sum())) / (N_SHIFT + 1)
    dev_obs = abs(high_obs - n * f_high)
    p_high = (1 + int((np.abs(high_null - n * f_high) >= dev_obs - 1e-12).sum())) / (N_SHIFT + 1)
    mu_n, sd_n = comp_null.mean(axis=0), comp_null.std(axis=0)
    z_obs = (comp_obs - mu_n) / sd_n
    z_null = (comp_null - mu_n) / sd_n
    p_sea = (1 + int((np.abs(z_null).max(axis=1) >= np.abs(z_obs).max() - 1e-12).sum())) / (N_SHIFT + 1)
    lo, hi = np.percentile(comp_null, [2.5, 97.5], axis=0)

    return {
        "id": sid,
        "label": label,
        "primary": primary,
        "vei_min": vei_min,
        "window": [float(y0), float(y1)],
        "n_events": int(n),
        "phase": {
            "bins": NB_PHASE,
            "observed": obs_counts.tolist(),
            "expected": exp_counts.tolist(),
            "chi2": chi_obs,
            "p": p_phase,
            "labels": ["tidlig stigende (0–25 %)", "sen stigende/maks (25–50 %)", "tidlig avtagende (50–75 %)", "sen avtagende/minimum (75–100 %)"],
        },
        "high_low": {
            "median_smoothed_ssn": float(median),
            "n_high": int(high_obs),
            "n_low": int(n - high_obs),
            "expected_share_high": f_high,
            "observed_share_high": high_obs / n if n else float("nan"),
            "p": p_high,
        },
        "sea": {
            "lags": LAGS,
            "composite_z": comp_obs.tolist(),
            "null_mean": mu_n.tolist(),
            "band_lo": lo.tolist(),
            "band_hi": hi.tolist(),
            "p_global": p_sea,
            "max_abs_z": float(np.abs(z_obs).max()),
            "n_lags": len(LAGS),
        },
    }


def analyse_volcano(cycles: list[dict], outdir=DATA_DIR) -> dict:
    rng = S.rng_for("volcano")
    e = read_json("volcano_eruptions.json", outdir)
    ev = {
        "t": _arr(e["t"]),
        "vei": np.array(e["vei"], dtype=int),
        "confirmed": np.array(e["confirmed"], dtype=bool),
        "precise": np.array(e.get("precise", [True] * len(e["t"])), dtype=bool),
        "year": np.array(e["year"], dtype=int),
    }
    sm = monthly_ssn(outdir)
    ssn_y = yearly_ssn(outdir)
    results = [run_scenario(*sc, ev, cycles, sm, ssn_y, rng) for sc in SCENARIOS]

    # Holm over de seks primærtestene (A og B: fase, høy/lav, SEA)
    prim = [r for r in results if r["primary"]]
    plist = []
    for r in prim:
        plist += [r["phase"]["p"], r["high_low"]["p"], r["sea"]["p_global"]]
    adj = S.holm(plist)
    for i, r in enumerate(prim):
        r["phase"]["p_holm"], r["high_low"]["p_holm"], r["sea"]["p_holm"] = adj[3 * i : 3 * i + 3]
    n_tests_total = 3 * len(results)

    # Rapporteringsskjevhet: antall bekreftede utbrudd per 50 år
    bins = list(range(1500, 2051, 50))
    reporting = {"bins": bins[:-1], "vei3": [], "vei4": [], "vei5": []}
    for b0, b1 in zip(bins[:-1], bins[1:]):
        m = ev["confirmed"] & (ev["year"] >= b0) & (ev["year"] < b1)
        reporting["vei3"].append(int((m & (ev["vei"] >= 3)).sum()))
        reporting["vei4"].append(int((m & (ev["vei"] >= 4)).sum()))
        reporting["vei5"].append(int((m & (ev["vei"] >= 5)).sum()))
    # Utbrudd per syklus (VEI≥4) for figur
    return _round(
        {
            "n_tests": n_tests_total,
            "n_primary_tests": 6,
            "n_shifts": N_SHIFT,
            "scenarios": results,
            "reporting": reporting,
            "min_p_primary_adjusted": float(min(adj)),
            "any_primary_significant": bool(min(adj) < 0.05),
        },
        4,
    )
