"""Total solinnstråling (TSI).

Primær (årlig, 1610–): NOAA Climate Data Record, NNLTSI v03r00 (NASA/NOAA/LASP modell), NetCDF4/HDF5.
Måling (daglig, 2018–): LASP LISIRD, TSIS-1 TIM (Level 3, 24-timers midler).

Verifisert 2026-10-31. PMOD-kompositten (pmodwrc.ch) har ingen maskinlesbar fil på en stabil URL (siden returnerer
HTML), og LISIRD-datasettet «composite_tsi» finnes ikke lenger (404) – derfor NOAA NCEI + TSIS-1.
"""

from __future__ import annotations

import io
import json
from datetime import datetime, timedelta

import h5py
import numpy as np
import pandas as pd

from ..core import Source, ValidationError, check_range, http_get, r

NCEI_DIR = "https://www.ncei.noaa.gov/data/total-solar-irradiance/access/yearly/"
TSIS_URL = "https://lasp.colorado.edu/lisird/latis/dap/tsis_tsi_24hr.json"


def _find_yearly_file(index_html: bytes) -> str:
    import re

    names = re.findall(rb'href="(tsi_v\d+r\d+_yearly_[^"]+\.nc)"', index_html)
    if not names:
        raise ValidationError("Fant ingen årlig TSI-fil i NCEI-katalogen")
    return sorted(n.decode() for n in names)[-1]


def _fetch():
    idx = http_get(NCEI_DIR)
    name = _find_yearly_file(idx)
    return {"nnl": http_get(NCEI_DIR + name, timeout=300), "nnl_name": name.encode(), "tsis": http_get(TSIS_URL, timeout=300)}


def parse_nnl(raw: bytes) -> pd.DataFrame:
    with h5py.File(io.BytesIO(raw), "r") as h:
        tsi = np.asarray(h["TSI"][:], dtype=float)
        unc = np.asarray(h["TSI_UNC"][:], dtype=float)
        bnds = np.asarray(h["time_bnds"][:], dtype=float)
    start = [datetime(1610, 1, 1) + timedelta(days=float(b[0])) for b in bnds]
    df = pd.DataFrame({"year": [d.year for d in start], "tsi": tsi, "unc": unc})
    df.loc[(df["tsi"] < 1300) | (df["tsi"] > 1400), "tsi"] = np.nan
    return df


def parse_tsis(raw: bytes) -> pd.DataFrame:
    obj = json.loads(raw)
    samples = obj["tsis_tsi_24hr"]["samples"]
    df = pd.DataFrame(samples)
    df = df[df["tsi_1au"] > 1300]  # første rad er en nullplassholder
    df["date"] = pd.to_datetime(df["time"], unit="D", origin="julian")
    df["ym"] = df["date"].dt.to_period("M")
    return df[["date", "ym", "tsi_1au", "instrument_accuracy_1au"]].reset_index(drop=True)


def _parse(raw):
    return {"nnl": parse_nnl(raw["nnl"]), "tsis": parse_tsis(raw["tsis"]), "nnl_name": raw["nnl_name"].decode()}


def _build(p):
    n, t = p["nnl"], p["tsis"]
    check_range(n["tsi"], 1355, 1370, "NNL TSI")
    check_range(t["tsi_1au"], 1355, 1370, "TSIS-1 TSI")
    if len(n) < 400:
        raise ValidationError(f"For få årlige TSI-verdier: {len(n)}")
    m = t.groupby("ym").agg(tsi=("tsi_1au", "mean"), n=("tsi_1au", "size")).reset_index()
    m = m[m["n"] >= 15]
    m["t"] = m["ym"].dt.year + (m["ym"].dt.month - 0.5) / 12
    files = {
        "tsi_yearly.json": {
            "source_file": p["nnl_name"],
            "year": [int(v) for v in n["year"]],
            "tsi": r(n["tsi"], 3),
            "unc": r(n["unc"], 3),
        },
        "tsi_tsis_monthly.json": {
            "t": r(m["t"], 3),
            "tsi": r(m["tsi"], 3),
            "days": [int(v) for v in m["n"]],
        },
    }
    return files, {"rows": len(n), "last_point": f"{int(n['year'].iloc[-1])} (NNL); {t['date'].max():%Y-%m-%d} (TSIS-1)"}


SOURCE = Source(
    id="tsi",
    name="Total solinnstråling: NOAA CDR NNLTSI (modell, 1610–) og TSIS-1 (måling, 2018–)",
    provider="NOAA NCEI / LASP (University of Colorado)",
    group="monthly",
    urls=[NCEI_DIR, TSIS_URL],
    homepage="https://www.ncei.noaa.gov/products/climate-data-records/total-solar-irradiance",
    license="NOAA CDR: åpne data, oppgi kilde. LASP LISIRD: åpne data, oppgi kilde.",
    citation=(
        "Coddington, O., Lean, J.L., Pilewskie, P., Snow, M. & Lindholm, D. (2016), A Solar Irradiance Climate Data Record, "
        "Bull. Amer. Meteor. Soc. 97, 1265–1282; NOAA CDR Program: Total Solar Irradiance, NNLTSI v03r00. "
        "TSIS-1 TIM: LASP/University of Colorado Boulder, LISIRD."
    ),
    frequency="NOAA CDR: årlig utgave med månedlige filer; TSIS-1: daglig. Hentes månedlig.",
    caveats=(
        "NNLTSI er en modell (proxy-basert, kalibrert mot satellittmålinger), ikke en måling før 1978. Korrelasjon med solflekktall "
        "er delvis bygget inn i modellen. Lange satellittkompositter (PMOD, ACRIM, RMIB) er uenige om trender mellom 1980- og 2000-tallet."
    ),
    fetch=_fetch,
    parse=_parse,
    build=_build,
    fallback_note="PMOD-komposittens datafil er ikke tilgjengelig maskinelt; erstattet av NOAA CDR (modell) + TSIS-1 (måling).",
)
