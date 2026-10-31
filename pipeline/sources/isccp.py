"""Skydekke: ISCCP-H (NOAA NCEI), månedlige globale gridfiler 1983-07 → 2017-06, brukt til å teste Svensmark-hypotesen.

Verifisert 2026-10-31:
  https://www.ncei.noaa.gov/data/international-satellite-cloud-climate-project-isccp-h-series-data/access/isccp-basic/hgm/
  408 NetCDF4-filer (~4 MB hver), 1°×1°, variabler cldamt (totalt skydekke, %), cldamt_irtypes (lav/midt/høy etter topptrykk).
  Lisens (filattributt): «No constraints on data access or use.» Pakket verdi = rå · 0,1 + 50; fyllverdi 32767.

Datasettet er avsluttet (siste måned 2017-06), og hele nedlastingen er ≈ 1,7 GB. Kilden har derfor gruppe «static»:
den kjøres bare manuelt (`python -m pipeline.run --only isccp`), ikke i de planlagte workflowene. Råfiler bufres i pipeline/.cache/isccp/.
Utdata er bare breddebånd-aggregater (areavektet), ikke rutenettet.
"""

from __future__ import annotations

import concurrent.futures as cf
import io
import json
import re
from datetime import datetime, timedelta

import h5py
import numpy as np
import pandas as pd

from ..core import ROOT, Source, ValidationError, check_range, http_get, r

BASE = "https://www.ncei.noaa.gov/data/international-satellite-cloud-climate-project-isccp-h-series-data/access/isccp-basic/hgm/"
CACHE = ROOT / "pipeline" / ".cache" / "isccp"
BANDS = {"global": (-90, 90), "ex_polar": (-60, 60), "tropics": (-30, 30), "midlat": None, "polar": None}
TYPES = ["total", "low", "mid", "high"]


def band_mask(lat: np.ndarray, band: str) -> np.ndarray:
    a = np.abs(lat)
    if band == "global":
        return np.ones_like(lat, bool)
    if band == "ex_polar":
        return a <= 60
    if band == "tropics":
        return a <= 30
    if band == "midlat":
        return (a > 30) & (a <= 60)
    if band == "polar":
        return a > 60
    raise KeyError(band)


def aggregate_file(raw: bytes) -> dict:
    """Én måned → {t, band: {type: areavektet middel}}. Pakket verdi: rå·0,1+50, fyllverdi 32767."""
    with h5py.File(io.BytesIO(raw), "r") as h:
        lat = np.asarray(h["lat"][:], float)
        days = float(h["time"][0])
        fields = {
            "total": np.asarray(h["cldamt"][0], float),
            "low": np.asarray(h["cldamt_irtypes"][0, 0], float),
            "mid": np.asarray(h["cldamt_irtypes"][0, 1], float),
            "high": np.asarray(h["cldamt_irtypes"][0, 2], float),
        }
    date = datetime(1970, 1, 1) + timedelta(days=days)
    out = {"t": date.year + (date.month - 0.5) / 12, "year": date.year, "month": date.month}
    w_lat = np.cos(np.deg2rad(lat))[:, None] * np.ones((1, 360))
    for band in BANDS:
        m = band_mask(lat, band)[:, None] * np.ones((1, 360), bool)
        res = {}
        for k, raw_field in fields.items():
            valid = (raw_field != 32767) & np.isfinite(raw_field) & m
            val = raw_field * 0.1 + 50
            val = np.where(valid, val, np.nan)
            ok = valid & (val >= 0) & (val <= 100)
            res[k] = float((val[ok] * w_lat[ok]).sum() / w_lat[ok].sum()) if ok.sum() > 50 else None
            res[k + "_cover"] = float(w_lat[ok].sum() / w_lat[m].sum())
        out[band] = res
    return out


def _fetch():
    listing = http_get(BASE).decode("utf-8", errors="replace")
    names = sorted(set(re.findall(r'href="(ISCCP-Basic\.HGM[^"]+\.nc)"', listing)))
    if len(names) < 400:
        raise ValidationError(f"ISCCP-H: forventet ≥ 400 månedsfiler, fant {len(names)}")
    CACHE.mkdir(parents=True, exist_ok=True)

    def one(name: str) -> dict:
        p = CACHE / name
        if p.exists() and p.stat().st_size > 1_000_000:
            return aggregate_file(p.read_bytes())
        raw = http_get(BASE + name, timeout=180)
        p.write_bytes(raw)
        return aggregate_file(raw)

    with cf.ThreadPoolExecutor(8) as ex:
        rows = list(ex.map(one, names))
    return {"agg": json.dumps(rows).encode()}


def _parse(raw):
    rows = json.loads(raw["agg"])
    df = pd.DataFrame({"t": [x["t"] for x in rows], "year": [x["year"] for x in rows], "month": [x["month"] for x in rows]})
    for band in BANDS:
        for k in TYPES:
            df[f"{band}_{k}"] = [x[band][k] for x in rows]
            df[f"{band}_{k}_cover"] = [x[band][k + "_cover"] for x in rows]
    return {"df": df.sort_values("t").reset_index(drop=True)}


def _build(p):
    df = p["df"]
    check_range(df["global_total"], 30, 90, "ISCCP globalt skydekke (%)")
    check_range(df["global_low"], 5, 60, "ISCCP lavt skydekke (%)")
    if len(df) < 400:
        raise ValidationError(f"For få måneder: {len(df)}")
    out = {"t": r(df["t"], 3)}
    for band in BANDS:
        out[band] = {k: r(df[f"{band}_{k}"], 3) for k in TYPES}
    out["type_definition"] = {"low": "toppunkt-trykk > 680 hPa", "mid": "440–680 hPa", "high": "≤ 440 hPa (ISCCP IR-typer)"}
    last = df.iloc[-1]
    return {"cloud_isccp_monthly.json": out}, {"rows": len(df), "last_point": f"{int(last['year'])}-{int(last['month']):02d}"}


SOURCE = Source(
    id="isccp",
    name="Skydekke (totalt, lavt, midt, høyt): ISCCP-H månedlige 1°-data, 1983–2017",
    provider="NOAA NCEI – International Satellite Cloud Climatology Project (ISCCP) H-serie",
    group="static",
    urls=[BASE],
    homepage="https://www.ncei.noaa.gov/products/climate-data-records/cloud-properties-isccp",
    license="Ingen begrensninger på tilgang og bruk (filattributt); oppgi kilde og siter Rossow & Schiffer (1999).",
    citation=(
        "Young, A.H., Knapp, K.R., Inamdar, A., Hankins, W. & Rossow, W.B. (2018), The International Satellite Cloud Climatology Project H-Series "
        "climate data record product, Earth System Science Data 10, 583–593; Rossow, W.B. & Schiffer, R.A. (1999), Advances in understanding clouds "
        "from ISCCP, Bulletin of the American Meteorological Society 80, 2261–2287."
    ),
    frequency="Datasettet er avsluttet (siste måned juni 2017). Kjøres manuelt.",
    caveats=(
        "Skydekke fra geostasjonære og polarbanesatellitter har kjente artefakter: endringer i satellitt, kalibrering og visningsvinkel gir "
        "kunstige trender (særlig i tropene og for lavt skydekke), så trender og lavfrekvente variasjoner må tolkes med forsiktighet (Evan m.fl. 2007). "
        "Lavt skydekke maskeres delvis av høye skyer. Serien dekker bare omtrent tre solsykluser."
    ),
    fetch=_fetch,
    parse=_parse,
    build=_build,
    fallback_note="PATMOS-x (daglige filer, svært store), CM SAF CLARA (krever bestilling) og NCEP-reanalyse (modell, ikke måling) ble vurdert, men ikke brukt.",
)
