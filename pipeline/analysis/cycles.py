"""Solsyklusdeteksjon fra glattet månedlig solflekktall (SILSO V2.0, 13-måneders glatting)."""

from __future__ import annotations

import numpy as np
from scipy.signal import argrelextrema


def detect_minima(t: np.ndarray, smoothed: np.ndarray, order_months: int = 36, min_sep_years: float = 7.0) -> list[int]:
    """Indekser for syklusminima. Lokale minima (±order_months), og av minima nærmere enn min_sep_years beholdes det laveste."""
    ok = np.isfinite(smoothed)
    idx_all = np.where(ok)[0]
    s = smoothed[idx_all]
    loc = argrelextrema(s, np.less_equal, order=order_months)[0]
    cand = [int(idx_all[i]) for i in loc]
    # fjern flate duplikater / for tette minima
    kept: list[int] = []
    for i in cand:
        if kept and t[i] - t[kept[-1]] < min_sep_years:
            if smoothed[i] < smoothed[kept[-1]]:
                kept[-1] = i
        else:
            kept.append(i)
    return kept


def build_cycles(t: np.ndarray, smoothed: np.ndarray) -> list[dict]:
    """Syklus 1 begynner ved første påviste minimum etter 1749 (mars 1755). Siste syklus er ufullstendig."""
    mins = detect_minima(t, smoothed)
    cycles = []
    for k, i0 in enumerate(mins):
        i1 = mins[k + 1] if k + 1 < len(mins) else None
        seg_end = i1 if i1 is not None else len(t)
        seg = smoothed[i0:seg_end]
        if not np.isfinite(seg).any():
            continue
        j = int(np.nanargmax(seg))
        cycles.append(
            {
                "n": k + 1,
                "start_t": float(t[i0]),
                "end_t": float(t[i1]) if i1 is not None else None,
                "length_years": float(t[i1] - t[i0]) if i1 is not None else None,
                "max_t": float(t[i0 + j]),
                "max_smoothed": float(seg[j]),
                "min_start_value": float(smoothed[i0]),
                "rise_years": float(t[i0 + j] - t[i0]),
                "complete": i1 is not None,
            }
        )
    return cycles


def phase_of(times: np.ndarray, cycles: list[dict]) -> np.ndarray:
    """Fase 0..1 i solsyklusen for hvert tidspunkt (NaN utenfor fullførte sykluser)."""
    out = np.full(len(times), np.nan)
    for c in cycles:
        if not c["complete"]:
            continue
        m = (times >= c["start_t"]) & (times < c["end_t"])
        out[m] = (times[m] - c["start_t"]) / (c["end_t"] - c["start_t"])
    return out
