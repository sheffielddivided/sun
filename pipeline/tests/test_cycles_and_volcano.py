import numpy as np
import pytest

from pipeline.analysis import cycles as C
from pipeline.sources import silso


def test_cycle_detection_matches_known_minima(fx):
    df = silso.parse_monthly(fx("SN_ms_tot_V2.0.1749-1907.csv"))
    cy = C.build_cycles(df["t"].to_numpy(), df["ssn"].to_numpy())
    starts = [round(c["start_t"], 1) for c in cy]
    # Kjente minima (SILSO): mars 1755, juni 1766, ... – toleranse ±0,6 år
    known = [1755.2, 1766.5, 1775.5, 1784.7, 1798.3, 1810.6, 1823.3, 1833.9, 1843.5, 1856.0, 1867.2, 1878.9, 1890.2, 1902.0]
    assert len(cy) >= 14
    for got, want in zip(starts, known):
        assert got == pytest.approx(want, abs=0.6)
    assert cy[0]["n"] == 1
    # Syklus 3 (1778) var den høyeste tidlige syklusen
    assert max(cy[:5], key=lambda c: c["max_smoothed"])["n"] == 3


def test_phase_of_range():
    cycles = [
        {"n": 1, "start_t": 1755.0, "end_t": 1766.0, "complete": True},
        {"n": 2, "start_t": 1766.0, "end_t": None, "complete": False},
    ]
    ph = C.phase_of(np.array([1754.0, 1755.0, 1760.5, 1765.99, 1770.0]), cycles)
    assert np.isnan(ph[0]) and ph[1] == 0 and ph[2] == pytest.approx(0.5) and ph[3] < 1 and np.isnan(ph[4])


def test_volcano_scenario_detects_planted_phase_locking_and_not_random():
    from pipeline.analysis import volcano as V

    # Syntetiske, uregelmessige sykluser (9–13 år) fra 1850. Med eksakt periodiske sykluser er sirkulære skift ikke informative.
    lg = np.random.default_rng(5)
    lengths = lg.uniform(9, 13, size=14)
    starts = 1850 + np.concatenate([[0], np.cumsum(lengths)])
    t = np.arange(1849.5, starts[-1] - 1, 1 / 12)

    def activity(x):
        k = np.clip(np.searchsorted(starts, x, side="right") - 1, 0, len(lengths) - 1)
        return 100 + 80 * np.sin(2 * np.pi * (x - starts[k]) / lengths[k] - np.pi / 2)

    sm = activity(t)
    mon = {"t": t, "smoothed": sm, "ssn": sm}
    cycles = [{"n": k + 1, "start_t": float(starts[k]), "end_t": float(starts[k + 1]), "complete": True, "length_years": float(lengths[k])} for k in range(13)]
    cycles.append({"n": 14, "start_t": float(starts[13]), "end_t": None, "complete": False})
    ssn_y = {int(y): float(activity(y + 0.5)) for y in range(1700, int(starts[-1]))}
    rng = np.random.default_rng(11)
    V.N_SHIFT = 1500
    n = 120

    def make(times):
        return {"t": np.array(times), "vei": np.full(len(times), 4), "confirmed": np.ones(len(times), bool), "precise": np.ones(len(times), bool)}

    # (a) alle utbrudd rett etter minimum (fase 0–0,25) → klar fasekobling
    locked = make([starts[k] + rng.uniform(0, 0.2) * lengths[k] for k in rng.integers(0, 13, size=n)])
    r1 = V.run_scenario("T", "test", 4, None, None, False, True, locked, cycles, mon, ssn_y, rng)
    assert r1["phase"]["p"] < 0.01 and r1["high_low"]["p"] < 0.05
    # (b) jevnt tilfeldige utbrudd → ingen kobling (p ikke ekstremt liten)
    ps = []
    for seed in range(6):
        rr = np.random.default_rng(100 + seed)
        rand = make(list(rr.uniform(1850, starts[13], size=n)))
        r2 = V.run_scenario("T", "test", 4, None, None, False, True, rand, cycles, mon, ssn_y, rr)
        ps.append(r2["phase"]["p"])
    assert np.mean(np.array(ps) < 0.01) < 0.5


def test_spurious_demo_runs_small(tmp_path):
    from pipeline.analysis import context
    from pipeline.core import write_json

    yrs = list(range(1900, 2026))
    write_json("ssn_yearly.json", {"year": yrs, "ssn": [float(100 + 60 * np.sin(2 * np.pi * (y - 1900) / 11)) for y in yrs]}, tmp_path)
    res = context.analyse_spurious(tmp_path, n_sim=30, n_surr=49, n_dredge=50)
    walk = res["scenarios"][3]  # to uavhengige tilfeldige vandringer
    assert walk["false_positive_naive"] >= walk["false_positive_surrogate"]
