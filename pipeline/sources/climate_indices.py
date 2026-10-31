"""NAO og ENSO (ONI) fra NOAA Climate Prediction Center.

Verifiserte URL-er (2026-10-31):
  https://www.cpc.ncep.noaa.gov/products/precip/CWlink/pna/norm.nao.monthly.b5001.current.ascii   (år mnd verdi)
  https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt                                         (SEAS YR TOTAL ANOM)
"""

from __future__ import annotations

import re

import pandas as pd

from ..core import Source, ValidationError, check_range, ensure_not_html, http_get, r

NAO = "https://www.cpc.ncep.noaa.gov/products/precip/CWlink/pna/norm.nao.monthly.b5001.current.ascii"
ONI = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"
# Hver tre-måneders sesong tilordnes midtmåneden (DJF → januar, ..., NDJ → desember).
SEASON_CENTER = {s: i + 1 for i, s in enumerate(["DJF", "JFM", "FMA", "MAM", "AMJ", "MJJ", "JJA", "JAS", "ASO", "SON", "OND", "NDJ"])}


def parse_nao(raw: bytes) -> pd.DataFrame:
    rows = []
    for line in raw.decode("utf-8", errors="replace").splitlines():
        m = re.match(r"^\s*(\d{4})\s+(\d{1,2})\s+(-?\d+\.\d+)\s*$", line)
        if m:
            y, mo, v = int(m[1]), int(m[2]), float(m[3])
            rows.append((y, mo, y + (mo - 0.5) / 12, v))
    if not rows:
        raise ValidationError("NAO: ingen datalinjer")
    return pd.DataFrame(rows, columns=["year", "month", "t", "nao"])


def parse_oni(raw: bytes) -> pd.DataFrame:
    """ONI er et tre-måneders glidende middel (SEAS YR TOTAL ANOM). Sesongen tilordnes midtmåneden."""
    rows = []
    for line in raw.decode("utf-8", errors="replace").splitlines():
        parts = line.split()
        if len(parts) == 4 and parts[0] in SEASON_CENTER and re.fullmatch(r"\d{4}", parts[1]):
            mo = SEASON_CENTER[parts[0]]
            y = int(parts[1])
            rows.append((y, mo, y + (mo - 0.5) / 12, float(parts[3])))
    if not rows:
        raise ValidationError("ONI: ingen datalinjer")
    df = pd.DataFrame(rows, columns=["year", "month", "t", "oni"])
    return df.sort_values("t").reset_index(drop=True)


def _fetch():
    return {
        "nao": ensure_not_html(http_get(NAO), "norm.nao.monthly"),
        "oni": ensure_not_html(http_get(ONI), "oni.ascii.txt"),
    }


def _parse(raw):
    return {"nao": parse_nao(raw["nao"]), "oni": parse_oni(raw["oni"])}


def _build(p):
    n, o = p["nao"], p["oni"]
    check_range(n["nao"], -6, 6, "NAO")
    check_range(o["oni"], -4, 4, "ONI")
    if len(n) < 700 or len(o) < 700:
        raise ValidationError(f"For få verdier: NAO {len(n)}, ONI {len(o)}")
    files = {
        "nao_monthly.json": {"t": r(n["t"], 3), "nao": r(n["nao"], 2)},
        "oni_monthly.json": {"t": r(o["t"], 3), "oni": r(o["oni"], 2)},
    }
    return files, {"rows": len(n) + len(o), "last_point": f"NAO {int(n.iloc[-1]['year'])}-{int(n.iloc[-1]['month']):02d}; ONI {int(o.iloc[-1]['year'])}-{int(o.iloc[-1]['month']):02d}"}


SOURCE = Source(
    id="climate_indices",
    name="NAO (månedlig) og ENSO (Oceanic Niño Index)",
    provider="NOAA Climate Prediction Center",
    group="monthly",
    urls=[NAO, ONI],
    homepage="https://www.cpc.ncep.noaa.gov/",
    license="Offentlig eie (U.S. Government work). Oppgi NOAA CPC som kilde.",
    citation="NOAA Climate Prediction Center: North Atlantic Oscillation index (1950–) og Oceanic Niño Index (ONI). https://www.cpc.ncep.noaa.gov/",
    frequency="Månedlig.",
    caveats="Seriene starter i 1950, så de dekker bare fem solsykluser; statistisk kraft er derfor lav. ONI er et tre-måneders glidende middel, noe som øker autokorrelasjonen.",
    fetch=_fetch,
    parse=_parse,
    build=_build,
)
