"""GFZ Potsdam: Kp/ap siden 1932 → månedlige geomagnetiske aggregater.

Verifisert URL (2026-10-31): https://kp.gfz-potsdam.de/app/files/Kp_ap_since_1932.txt (≈16 MB, CC BY 4.0).
Den gamle datapub-URL-en (datapub.gfz-potsdam.de/download/10.5880.Kp.0001/...) gir 404.
"""

from __future__ import annotations

import pandas as pd

from ..core import Source, ValidationError, check_range, ensure_not_html, http_get, r
from .swpc import parse_gfz_kp

URL = "https://kp.gfz-potsdam.de/app/files/Kp_ap_since_1932.txt"


def _fetch():
    return {"kp": ensure_not_html(http_get(URL, timeout=300), "Kp_ap_since_1932.txt")}


def _parse(raw):
    return {"kp": parse_gfz_kp(raw["kp"])}


def monthly_aggregates(df: pd.DataFrame) -> pd.DataFrame:
    """Aggreger 3-timers Kp/ap til måneder. `storm_days` = døgn med maks-Kp ≥ 5 (NOAA G1 eller sterkere),
    `severe_days` = døgn med maks-Kp ≥ 7 (G3 eller sterkere)."""
    d = df.dropna(subset=["kp"]).copy()
    d["date"] = d["time"].dt.floor("D")
    daily = d.groupby("date").agg(kpmax=("kp", "max"), kpmean=("kp", "mean"), apmean=("ap", "mean"), n=("kp", "size"))
    daily = daily[daily["n"] >= 6]  # kun nesten komplette døgn
    daily["ym"] = daily.index.to_period("M")
    g = daily.groupby("ym").agg(
        kp_mean=("kpmean", "mean"),
        ap_mean=("apmean", "mean"),
        storm_days=("kpmax", lambda s: int((s >= 5 - 1e-9).sum())),
        severe_days=("kpmax", lambda s: int((s >= 7 - 1e-9).sum())),
        days=("kpmax", "size"),
    )
    g = g.reset_index()
    g["year"] = g["ym"].dt.year
    g["month"] = g["ym"].dt.month
    g["t"] = g["year"] + (g["month"] - 0.5) / 12
    return g


def _build(p):
    df = p["kp"]
    check_range(df["kp"], 0, 9.01, "Kp")
    if len(df) < 250_000:
        raise ValidationError(f"For få Kp-rader: {len(df)}")
    g = monthly_aggregates(df)
    files = {
        "geomag_monthly.json": {
            "t": r(g["t"], 3),
            "year": [int(v) for v in g["year"]],
            "month": [int(v) for v in g["month"]],
            "kp_mean": r(g["kp_mean"], 3),
            "ap_mean": r(g["ap_mean"], 2),
            "storm_days": [int(v) for v in g["storm_days"]],
            "severe_days": [int(v) for v in g["severe_days"]],
            "days": [int(v) for v in g["days"]],
        }
    }
    last = g.iloc[-1]
    return files, {"rows": len(df), "last_point": f"{int(last['year'])}-{int(last['month']):02d}"}


SOURCE = Source(
    id="gfz_kp",
    name="Geomagnetiske indekser Kp og ap siden 1932 (månedlige aggregater)",
    provider="GFZ Helmholtz Centre for Geosciences, Potsdam (Geomagnetic Observatory Niemegk)",
    group="monthly",
    urls=[URL],
    homepage="https://kp.gfz-potsdam.de/en/data",
    license="CC BY 4.0",
    citation=(
        "Matzka, J., Stolle, C., Yamazaki, Y., Bronkalla, O. & Morschhauser, A. (2021), The geomagnetic Kp index and derived "
        "indices of geomagnetic activity, Space Weather 19, e2020SW002641. https://doi.org/10.1029/2020SW002641"
    ),
    frequency="Løpende (nowcast) med endelige verdier etter hvert; hentes månedlig.",
    caveats="Kp er en kvasi-logaritmisk indeks fra stasjoner på midlere breddegrader og måler ikke nordlys direkte. De siste ukene er nowcast-verdier.",
    fetch=_fetch,
    parse=_parse,
    build=_build,
)
