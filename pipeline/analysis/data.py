"""Innlasting av de genererte JSON-seriene som regulære, justerte arrays for analysene."""

from __future__ import annotations

import numpy as np

from ..core import DATA_DIR, read_json


def _arr(v) -> np.ndarray:
    return np.array([np.nan if x is None else x for x in v], dtype=float)


def monthly_ssn(outdir=DATA_DIR) -> dict:
    d = read_json("ssn_monthly.json", outdir)
    return {"t": _arr(d["t"]), "ssn": _arr(d["ssn"]), "smoothed": _arr(d["smoothed"])}


def yearly_ssn(outdir=DATA_DIR) -> dict[int, float]:
    d = read_json("ssn_yearly.json", outdir)
    return {int(y): v for y, v in zip(d["year"], _arr(d["ssn"])) if np.isfinite(v)}


def annual_from_monthly(t: np.ndarray, v: np.ndarray, min_months: int = 12) -> dict[int, float]:
    years = np.floor(t + 1e-9).astype(int)
    out = {}
    for y in np.unique(years):
        m = (years == y) & np.isfinite(v)
        if m.sum() >= min_months:
            out[int(y)] = float(v[m].mean())
    return out


def align(*series: dict[int, float], y0: int | None = None, y1: int | None = None) -> tuple[np.ndarray, list[np.ndarray]]:
    """Felles år (uten hull) for flere {år: verdi}. Returnerer (år, [arrays])."""
    common = set(series[0])
    for s in series[1:]:
        common &= set(s)
    years = sorted(y for y in common if (y0 is None or y >= y0) and (y1 is None or y <= y1))
    # sørg for sammenhengende år (ingen hull) ved å ta lengste sammenhengende blokk
    best, cur = [], []
    for y in years:
        if cur and y != cur[-1] + 1:
            best = cur if len(cur) > len(best) else best
            cur = []
        cur.append(y)
    best = cur if len(cur) > len(best) else best
    yrs = np.array(best, dtype=int)
    return yrs, [np.array([s[int(y)] for y in yrs], dtype=float) for s in series]
