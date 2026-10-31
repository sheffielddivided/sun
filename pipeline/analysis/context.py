"""Historisk kontekst (Maunder-minimum) og demonstrasjon av tilfeldige korrelasjoner."""

from __future__ import annotations

import numpy as np

from ..core import DATA_DIR, read_json
from . import stats as S
from .data import _arr, yearly_ssn
from .solar_earth import _round


def _mean_between(d: dict[int, float], a: int, b: int) -> float | None:
    v = [x for y, x in d.items() if a <= y <= b and x is not None and np.isfinite(x)]
    return float(np.mean(v)) if v else None


def analyse_maunder(outdir=DATA_DIR) -> dict:
    g = read_json("group_yearly.json", outdir)
    bb = {int(y): v for y, v in zip(g["year"], _arr(g["backbone"])) if np.isfinite(v)}
    hs = {int(y): v for y, v in zip(g["year"], _arr(g["hs"])) if np.isfinite(v)}
    tsi = read_json("tsi_yearly.json", outdir)
    nnl = {int(y): v for y, v in zip(tsi["year"], _arr(tsi["tsi"])) if np.isfinite(v)}
    iv = read_json("volcano_forcing_ivi2.json", outdir)
    inj = {int(y): v for y, v in zip(iv["year"], _arr(iv["global_tg"]))}

    periods = {"maunder": (1645, 1715), "after": (1716, 1790), "dalton": (1790, 1830), "modern": (1950, 1995)}
    gn = {k: {"backbone": _mean_between(bb, a, b), "hs": _mean_between(hs, a, b)} for k, (a, b) in periods.items()}
    tsi_means = {k: _mean_between(nnl, a, b) for k, (a, b) in periods.items()}
    # Antall år med ≈ ingen observerte grupper (Gn < 0,5) – Maunder vs senere
    low_years = {k: sum(1 for y, v in hs.items() if a <= y <= b and v < 0.5) for k, (a, b) in periods.items()}
    # Vulkansk injeksjon
    top = sorted(((y, v) for y, v in inj.items() if 1500 <= y <= 1900), key=lambda t: -t[1])[:10]
    cent = {f"{c}": float(sum(v for y, v in inj.items() if c <= y < c + 100)) for c in (1500, 1600, 1700, 1800)}
    maun_inj = float(sum(v for y, v in inj.items() if 1645 <= y <= 1715))
    nxt_inj = float(sum(v for y, v in inj.items() if 1716 <= y <= 1786))
    n_big = {k: sum(1 for y, v in inj.items() if a <= y <= b and v >= 10) for k, (a, b) in {"1600_1700": (1600, 1699), "1700_1800": (1700, 1799), "1800_1900": (1800, 1899)}.items()}
    # Tidsserie for figur (1600–1900)
    ys = list(range(1600, 1901))
    return _round(
        {
            "n_tests": 0,
            "periods": {k: list(v) for k, v in periods.items()},
            "mean_group_number": gn,
            "mean_tsi_nnl": tsi_means,
            "tsi_diff_maunder_vs_modern": (tsi_means["modern"] - tsi_means["maunder"]) if tsi_means["maunder"] else None,
            "years_hs_below_half": low_years,
            "ivi2_top_years": [{"year": y, "global_tg": v} for y, v in top],
            "ivi2_century_sum_tg": cent,
            "ivi2_maunder_sum_tg": maun_inj,
            "ivi2_next_75y_sum_tg": nxt_inj,
            "ivi2_n_years_ge10tg": n_big,
            "series": {"year": ys, "ivi2_global_tg": [inj.get(y) for y in ys], "gn_backbone": [bb.get(y) for y in ys], "gn_hs": [hs.get(y) for y in ys]},
        },
        3,
    )


# ---------------------------------------------------------------------------------------------------
def _ar1(n: int, phi: float, rng: np.random.Generator) -> np.ndarray:
    e = rng.normal(size=n)
    x = np.zeros(n)
    for i in range(1, n):
        x[i] = phi * x[i - 1] + e[i]
    return x


def analyse_spurious(outdir=DATA_DIR, n_sim: int = 400, n_surr: int = 199) -> dict:
    """Hvor ofte gir helt urelaterte serier «signifikante» korrelasjoner med solflekktallet?"""
    rng = S.rng_for("spurious")
    ssn = yearly_ssn(outdir)
    years = sorted(y for y in ssn if 1900 <= y <= 2025)
    x = np.array([ssn[y] for y in years], dtype=float)
    N = len(x)
    scenarios = []
    ex = None
    for name, gen in (
        ("Hvit støy", lambda: rng.normal(size=N)),
        ("Autokorrelert støy (AR1, φ = 0,7)", lambda: _ar1(N, 0.7, rng)),
        ("Tilfeldig vandring (som en trend)", lambda: np.cumsum(rng.normal(size=N))),
    ):
        naive = neff_hits = surr_hits = 0
        abs_r = []
        for _ in range(n_sim):
            y = gen()
            r = S.pearson(x, y)
            abs_r.append(abs(r))
            p_naive = S.neff_pvalue(r, N)
            naive += p_naive < 0.05
            neff = S.effective_n(x, y)
            neff_hits += S.neff_pvalue(r, neff) < 0.05
            Sx = S.phase_surrogates(x, n_surr, rng)
            rs = S.corr_matrix_rows(Sx, y)
            p_s = (1 + int((np.abs(rs) >= abs(r) - 1e-12).sum())) / (n_surr + 1)
            surr_hits += p_s < 0.05
            if name.startswith("Tilfeldig") and ex is None and abs(r) > 0.6:
                ex = {"year": years, "ssn": x.tolist(), "random_walk": y.tolist(), "r": r}
        # Sannsynlighet for minst én «signifikant» av 20 uavhengige kandidater (naiv test)
        scenarios.append(
            {
                "name": name,
                "n": N,
                "n_sim": n_sim,
                "false_positive_naive": naive / n_sim,
                "false_positive_neff": neff_hits / n_sim,
                "false_positive_surrogate": surr_hits / n_sim,
                "median_abs_r": float(np.median(abs_r)),
                "share_abs_r_gt_0_3": float(np.mean(np.array(abs_r) > 0.3)),
                "share_abs_r_gt_0_5": float(np.mean(np.array(abs_r) > 0.5)),
            }
        )
    p0 = scenarios[-1]["false_positive_naive"]
    # eksempel: hvis vi søker blant 20 urelaterte tilfeldig-vandring-serier
    at_least_one = 1 - (1 - p0) ** 20
    return _round(
        {
            "n_tests": n_sim * 3,
            "period": [years[0], years[-1]],
            "scenarios": scenarios,
            "at_least_one_of_20_naive_random_walk": at_least_one,
            "example": ex,
        },
        4,
    )
