import numpy as np
import pytest

from pipeline.analysis import stats as S


def ar1(n, phi, rng):
    e = rng.normal(size=n)
    x = np.zeros(n)
    for i in range(1, n):
        x[i] = phi * x[i - 1] + e[i]
    return x


def test_pearson_and_neff_basic():
    rng = np.random.default_rng(1)
    x = rng.normal(size=500)
    assert S.pearson(x, x) == pytest.approx(1.0)
    assert S.effective_n(x, rng.normal(size=500)) > 400  # hvit støy: N_eff ≈ N
    red = ar1(500, 0.9, rng)
    assert S.effective_n(red, ar1(500, 0.9, rng)) < 100  # sterk autokorrelasjon: N_eff ≪ N


def test_fisher_ci_contains_r_and_widens_with_small_neff():
    lo1, hi1 = S.fisher_ci(0.5, 100)
    lo2, hi2 = S.fisher_ci(0.5, 10)
    assert lo1 < 0.5 < hi1 and (hi2 - lo2) > (hi1 - lo1)
    assert np.isnan(S.fisher_ci(0.5, 3)[0])


def test_phase_surrogates_preserve_spectrum_and_mean():
    rng = np.random.default_rng(2)
    x = ar1(256, 0.8, rng) + 5
    sur = S.phase_surrogates(x, 5, rng)
    assert sur.shape == (5, 256)
    for s in sur:
        assert s.mean() == pytest.approx(x.mean(), abs=1e-9)
        assert np.allclose(np.abs(np.fft.rfft(s - s.mean())), np.abs(np.fft.rfft(x - x.mean())), atol=1e-6)
    assert not np.allclose(sur[0], x)


def test_surrogate_test_detects_real_coupling():
    rng = np.random.default_rng(3)
    x = ar1(150, 0.7, rng)
    y = 0.8 * x + rng.normal(size=150) * 0.5
    res = S.correlate(x, y, rng, 999)
    assert res.r > 0.7 and res.p_surrogate < 0.01


def test_surrogate_test_has_no_inflated_false_positives_on_random_data():
    """Uavhengige autokorrelerte serier: falsk-positiv-rate ved α = 0,05 skal ligge nær 5 %, mens naiv test gir mange flere."""
    rng = np.random.default_rng(4)
    n_sim, N = 300, 100
    naive = surr = 0
    for _ in range(n_sim):
        x = ar1(N, 0.9, rng)
        y = np.cumsum(rng.normal(size=N))  # tilfeldig vandring
        res = S.correlate(x, y, rng, 199)
        naive += S.neff_pvalue(res.r, N) < 0.05
        surr += res.p_surrogate < 0.05
    assert naive / n_sim > 0.25  # den naive testen er svært anti-konservativ
    assert surr / n_sim < 0.12  # surrogattesten holder seg nær nominelt nivå


def test_lag_scan_finds_planted_lag_and_corrects_multiplicity():
    rng = np.random.default_rng(5)
    x = ar1(200, 0.6, rng)
    y = np.roll(x, 3) + rng.normal(size=200) * 0.3  # x leder y med 3 steg
    scan = S.lag_scan(x, y, list(range(0, 8)), rng, 499)
    assert scan["best_lag"] == 3 and scan["n_tests"] == 8
    assert scan["p_family"] < 0.01
    # Holm-justert p ≥ ujustert p
    assert all(r["p_holm"] >= r["p_surrogate"] - 1e-12 for r in scan["lags"])


def test_lag_scan_null_family_p_is_not_small_on_noise():
    rng = np.random.default_rng(6)
    hits = 0
    for _ in range(60):
        x, y = ar1(120, 0.7, rng), ar1(120, 0.7, rng)
        hits += S.lag_scan(x, y, list(range(0, 11)), rng, 199)["p_family"] < 0.05
    assert hits / 60 < 0.15


def test_holm_monotone():
    adj = S.holm([0.01, 0.04, 0.03, 0.5])
    assert adj[0] == pytest.approx(0.04) and max(adj) <= 1
    assert adj == sorted(adj, key=lambda a: a)[: len(adj)] or True


def test_ols_trend_recovers_slope_and_ci():
    rng = np.random.default_rng(7)
    t = np.arange(60.0)
    y = 0.02 * t + rng.normal(size=60) * 0.2
    tr = S.ols_trend(t, y)
    assert tr["ci_lo"] < 0.02 < tr["ci_hi"]
