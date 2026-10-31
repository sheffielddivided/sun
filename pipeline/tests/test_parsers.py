"""Parsere testes mot lagrede utdrag av ekte filer (hentet 2026-10-31)."""

import numpy as np
import pytest

from pipeline.core import ValidationError
from pipeline.sources import butterfly, climate_indices, cosmic, gfz_kp, silso, swpc, temperature, tsi, volcanoes


def test_silso_monthly(fx):
    df = silso.parse_monthly(fx("SN_m_tot_V2.0.head.csv"))
    assert df["year"].iloc[0] == 1749 and df["month"].iloc[0] == 1
    assert df["ssn"].iloc[0] == pytest.approx(96.7)
    assert df["std"].isna().iloc[0]  # -1.0 → NaN
    assert df["definitive"].iloc[-1] in (0, 1)


def test_silso_smoothed_has_missing_edges(fx):
    df = silso.parse_monthly(fx("SN_ms_tot_V2.0.1749-1907.csv"))
    assert df["ssn"].iloc[:6].isna().all()  # 13-måneders glatting gir ingen verdi de første 6 månedene
    assert df["ssn"].iloc[6] == pytest.approx(135.9)


def test_silso_yearly(fx):
    df = silso.parse_yearly(fx("SN_y_tot_V2.0.excerpt.csv"))
    assert df["year"].iloc[0] == 1700 and df["ssn"].iloc[0] == pytest.approx(8.3)
    assert df["year"].iloc[-1] == 2025


def test_silso_daily_and_eisn(fx):
    d = silso.parse_daily(fx("SN_d_tot_V2.0.excerpt.csv"))
    assert d["date"].iloc[0].year == 1818 and np.isnan(d["ssn"].iloc[0])
    assert d["date"].iloc[-1].strftime("%Y-%m-%d") == "2026-09-30"
    e = silso.parse_eisn(fx("EISN_current.excerpt.csv"))
    assert e["ssn"].iloc[-1] == 27 and e["date"].iloc[-1].day == 31


def test_silso_hemispheric_and_groups(fx):
    h = silso.parse_hem_monthly(fx("SN_m_hem_V2.0.excerpt.csv"))
    assert h["north"].iloc[0] == pytest.approx(67.0) and h["south"].iloc[0] == pytest.approx(131.3)
    g = silso.parse_group_yearly(fx("GNbb2_y.excerpt.txt"))
    assert g["year"].iloc[0] == 1610 and g["gn"].iloc[0] == pytest.approx(2.64)


def test_html_error_page_is_rejected():
    from pipeline.core import ensure_not_html

    with pytest.raises(ValidationError):
        ensure_not_html(b"<!DOCTYPE html><html><head><title>404 Not Found</title>", "x")


def test_swpc_observed_and_prediction(fx):
    o = swpc.parse_observed(fx("observed-solar-cycle-indices.excerpt.json"))
    assert o["ssn"].iloc[0] == pytest.approx(96.7) and np.isnan(o["smoothed_ssn"].iloc[0])
    p = swpc.parse_prediction(fx("predicted-solar-cycle.excerpt.json"))
    assert p["t"].iloc[0] == pytest.approx(2026 + 3.5 / 12)


def test_swpc_daily_indices(fx):
    d = swpc.parse_daily_indices(fx("daily-solar-indices.excerpt.txt"))
    assert d["f107"].iloc[-1] == 90 and d["sesc_ssn"].iloc[-1] == 36
    assert d["date"].iloc[-1].strftime("%Y-%m-%d") == "2026-10-30"


def test_kp_gfz_nowcast_and_noaa(fx):
    k = swpc.parse_gfz_kp(fx("Kp_ap_nowcast.excerpt.txt"))
    assert len(k) > 5 and k["kp"].max() <= 9
    n = swpc.parse_noaa_kp(fx("noaa-planetary-k-index.excerpt.json"))
    assert len(n) == 6 and n["kp"].notna().all()


def test_gfz_monthly_aggregation(fx):
    df = swpc.parse_gfz_kp(fx("Kp_ap_since_1932.excerpt.txt"))
    g = gfz_kp.monthly_aggregates(df)
    assert g["year"].iloc[0] == 1932 and g["month"].iloc[0] == 1
    assert g["days"].iloc[0] == 31 and g["ap_mean"].iloc[0] > 0
    assert (g["storm_days"] >= 0).all()


def test_tsi_netcdf_and_tsis(fx):
    df = tsi.parse_nnl(fx("tsi_v03r00_monthly_s202501_e202512.nc"))
    assert len(df) == 12 and df["tsi"].between(1360, 1364).all() and df["year"].iloc[0] == 2025
    t = tsi.parse_tsis(fx("tsis_tsi_24hr.excerpt.json"))
    assert (t["tsi_1au"] > 1300).all() and len(t) >= 8  # nullplassholdere fjernet


def test_temperature(fx):
    g = temperature.parse_gistemp(fx("GLB.Ts+dSST.excerpt.csv"))
    assert g["year"].iloc[0] == 1880 and g["anom"].iloc[0] == pytest.approx(-0.19)
    assert g["anom"].notna().all()  # *** fjernet
    h = temperature.parse_hadcrut(fx("HadCRUT5.excerpt.csv"))
    assert h["year"].iloc[0] == 1850 and h["anom"].iloc[0] == pytest.approx(-0.67456436)


def test_oni_and_nao(fx):
    o = climate_indices.parse_oni(fx("oni.excerpt.txt"))
    assert (o["year"].iloc[0], o["month"].iloc[0]) == (1950, 1) and o["oni"].iloc[0] == pytest.approx(-1.32)
    n = climate_indices.parse_nao(fx("nao.excerpt.txt"))
    assert n["nao"].iloc[0] == pytest.approx(0.92)


def test_cosmic_phi(fx):
    d = cosmic.parse_phi(fx("Phi_mon.excerpt.txt"))
    assert d["year"].iloc[0] == 1936 and d["phi"].iloc[0] == 252 and d["month"].iloc[0] == 7  # Jan–Jun mangler i 1936


def test_gvp_eruptions(fx):
    d = volcanoes.parse_eruptions(fx("gvp_wfs.excerpt.json"))
    tamb = d[d["volcano"] == "Tambora"].iloc[-1]
    assert tamb["vei"] == 7 and tamb["year"] == 1812 and not tamb["precise"]  # flerårig episode → ikke presis
    pin = d[d["volcano"] == "Pinatubo"].iloc[-1]
    assert pin["vei"] == 6 and pin["year"] == 1991 and pin["precise"]


def test_butterfly(fx):
    rot, area = butterfly.parse_bfly(fx("bflydata.excerpt.txt"))
    assert rot[0] == 275 and area.shape[1] == 50 and area.min() >= 0
    assert butterfly.rotation_to_decimal_year(275) == pytest.approx(1874.35, abs=0.05)
    with pytest.raises(ValidationError):
        butterfly.parse_bfly(b"1 2 3 4")


def test_isccp_aggregate_file():
    """Syntetisk fil med samme struktur som ISCCP-H HGM (pakket: rå·0,1+50, fyllverdi 32767)."""
    import io

    import h5py
    import numpy as np

    from pipeline.sources import isccp

    buf = io.BytesIO()
    with h5py.File(buf, "w") as h:
        h["lat"] = np.arange(-89.5, 90, 1.0)
        h["time"] = np.array([4943.0])  # 1983-07-16
        packed = lambda pct: np.full((1, 180, 360), int(round((pct - 50) * 10)), dtype=np.int16)  # noqa: E731
        h["cldamt"] = packed(66.0)
        types = np.stack([packed(30.0)[0], packed(20.0)[0], packed(13.0)[0]])[None]
        types[0, 0, :10, :] = 32767  # manglende data nær sørpolen
        h["cldamt_irtypes"] = types
    out = isccp.aggregate_file(buf.getvalue())
    assert out["year"] == 1983 and out["month"] == 7
    assert out["global"]["total"] == pytest.approx(66.0, abs=0.01)
    assert out["global"]["low"] == pytest.approx(30.0, abs=0.01)
    assert out["tropics"]["high"] == pytest.approx(13.0, abs=0.01)
    assert out["polar"]["low_cover"] < 1.0  # manglende celler reduserer dekningen
