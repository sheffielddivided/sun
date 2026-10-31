"""NOAA SWPC (observert/prognose for syklus 25, F10.7) og Kp siste 30 dager (GFZ, reserve NOAA).

Verifiserte URL-er (hentet 2026-10-31):
  https://services.swpc.noaa.gov/json/solar-cycle/observed-solar-cycle-indices.json
  https://services.swpc.noaa.gov/json/solar-cycle/predicted-solar-cycle.json
  https://services.swpc.noaa.gov/text/daily-solar-indices.txt        (siste 30 dager, F10.7)
  https://kp.gfz-potsdam.de/app/files/Kp_ap_nowcast.txt               (Kp, 3-timers, ca. 30 dager)
  https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json (reserve; bare 7 dager)
"""

from __future__ import annotations

import io
import json
import re

import numpy as np
import pandas as pd

from ..core import Source, ValidationError, check_range, ensure_not_html, http_get, r

SWPC = "https://services.swpc.noaa.gov"
GFZ_NOW = "https://kp.gfz-potsdam.de/app/files/Kp_ap_nowcast.txt"

SWPC_LICENSE = "Offentlig eie (U.S. Government work). Be om at NOAA/SWPC oppgis som kilde."
SWPC_CITE = "NOAA Space Weather Prediction Center (SWPC). https://www.swpc.noaa.gov/"


def _ym_to_t(s: str) -> float:
    y, m = s.split("-")[:2]
    return int(y) + (int(m) - 0.5) / 12


# --------------------------------------------------------------------------
def parse_observed(raw: bytes) -> pd.DataFrame:
    data = json.loads(raw)
    df = pd.DataFrame(data)
    if "time-tag" not in df or "ssn" not in df:
        raise ValidationError("observed-solar-cycle-indices: forventede kolonner mangler")
    df["t"] = df["time-tag"].map(_ym_to_t)
    for c in df.columns:
        if c not in ("time-tag", "t"):
            df[c] = pd.to_numeric(df[c], errors="coerce").where(lambda s: s >= 0)
    return df


def parse_prediction(raw: bytes) -> pd.DataFrame:
    df = pd.DataFrame(json.loads(raw))
    if "time-tag" not in df or "predicted_ssn" not in df:
        raise ValidationError("predicted-solar-cycle: forventede kolonner mangler")
    df["t"] = df["time-tag"].map(_ym_to_t)
    return df


def _fetch_cycle():
    return {
        "obs": http_get(f"{SWPC}/json/solar-cycle/observed-solar-cycle-indices.json"),
        "pred": http_get(f"{SWPC}/json/solar-cycle/predicted-solar-cycle.json"),
    }


def _parse_cycle(raw):
    return {"obs": parse_observed(raw["obs"]), "pred": parse_prediction(raw["pred"])}


def _build_cycle(p):
    o, pr = p["obs"], p["pred"]
    check_range(o["ssn"], 0, 500, "NOAA observert ssn")
    check_range(pr["predicted_ssn"], 0, 400, "NOAA prognose ssn")
    if len(o) < 3000:
        raise ValidationError("For få rader i observed-solar-cycle-indices")
    f = o.dropna(subset=["f10.7"])
    files = {
        "f107_monthly.json": {"t": r(f["t"], 3), "f107": r(f["f10.7"], 1)},
        "cycle25_forecast.json": {
            "issued_from": pr["time-tag"].iloc[0],
            "t": r(pr["t"], 3),
            "ssn": r(pr["predicted_ssn"], 1),
            "ssn_low": r(pr["low_ssn"], 1),
            "ssn_high": r(pr["high_ssn"], 1),
            "f107": r(pr["predicted_f10.7"], 1),
            "f107_low": r(pr["low_f10.7"], 1),
            "f107_high": r(pr["high_f10.7"], 1),
        },
    }
    return files, {"rows": len(o), "last_point": o["time-tag"].iloc[-1]}


# --------------------------------------------------------------------------
def parse_daily_indices(raw: bytes) -> pd.DataFrame:
    """Tekstformat: «YYYY MM DD flux sesc_ssn area newreg field bkgd C M X ...» etter kommentarlinjer."""
    rows = []
    for line in raw.decode("utf-8", errors="replace").splitlines():
        if re.match(r"^\s*\d{4}\s+\d{2}\s+\d{2}\s", line):
            parts = line.split()
            rows.append((int(parts[0]), int(parts[1]), int(parts[2]), float(parts[3]), float(parts[4])))
    if not rows:
        raise ValidationError("Ingen datalinjer i daily-solar-indices.txt")
    df = pd.DataFrame(rows, columns=["year", "month", "day", "f107", "sesc_ssn"])
    df["date"] = pd.to_datetime(df[["year", "month", "day"]])
    df["f107"] = df["f107"].where(df["f107"] > 0)
    df["sesc_ssn"] = df["sesc_ssn"].where(df["sesc_ssn"] >= 0)
    return df


def _fetch_recent():
    return {"dsi": ensure_not_html(http_get(f"{SWPC}/text/daily-solar-indices.txt"), "daily-solar-indices")}


def _parse_recent(raw):
    return {"dsi": parse_daily_indices(raw["dsi"])}


def _build_recent(p):
    d = p["dsi"]
    check_range(d["f107"], 40, 500, "F10.7")
    if len(d) < 20:
        raise ValidationError(f"For få dager i daily-solar-indices: {len(d)}")
    files = {
        "recent30.json": {
            "date": [x.strftime("%Y-%m-%d") for x in d["date"]],
            "f107": r(d["f107"], 0),
            "sesc_ssn": r(d["sesc_ssn"], 0),
        }
    }
    return files, {"rows": len(d), "last_point": d["date"].iloc[-1].strftime("%Y-%m-%d")}


# --------------------------------------------------------------------------
def parse_gfz_kp(raw: bytes) -> pd.DataFrame:
    """GFZ-format: «YYYY MM DD hh.h hh._m days days_m Kp ap D» (kommentarer med #). Kp = -1: ikke tilgjengelig."""
    txt = raw.decode("utf-8", errors="replace")
    lines = [ln for ln in txt.splitlines() if ln.strip() and not ln.lstrip().startswith("#")]
    df = pd.read_csv(io.StringIO("\n".join(lines)), sep=r"\s+", header=None, engine="python")
    if df.shape[1] < 9:
        raise ValidationError(f"GFZ Kp: forventet ≥9 kolonner, fikk {df.shape[1]}")
    df = df.iloc[:, :9]
    df.columns = ["year", "month", "day", "hour", "hour_m", "days", "days_m", "kp", "ap"]
    df = df.apply(pd.to_numeric, errors="coerce").dropna(subset=["year", "month", "day", "hour"])
    df["time"] = pd.to_datetime(df[["year", "month", "day"]].astype(int)) + pd.to_timedelta(df["hour"], unit="h")
    df["kp"] = df["kp"].where(df["kp"] >= 0)
    df["ap"] = df["ap"].where(df["ap"] >= 0)
    return df.reset_index(drop=True)


def parse_noaa_kp(raw: bytes) -> pd.DataFrame:
    df = pd.DataFrame(json.loads(raw))
    df["time"] = pd.to_datetime(df["time_tag"])
    df["kp"] = pd.to_numeric(df["Kp"], errors="coerce")
    return df[["time", "kp"]]


def _fetch_kp():
    try:
        return {"gfz": ensure_not_html(http_get(GFZ_NOW), "Kp_ap_nowcast.txt")}
    except Exception:  # noqa: BLE001 – reserve
        return {"noaa": http_get(f"{SWPC}/products/noaa-planetary-k-index.json")}


def _parse_kp(raw):
    if "gfz" in raw:
        return {"kp": parse_gfz_kp(raw["gfz"]).dropna(subset=["kp"]), "origin": "GFZ Potsdam (nowcast)"}
    return {"kp": parse_noaa_kp(raw["noaa"]).dropna(subset=["kp"]), "origin": "NOAA SWPC (reserve, 7 dager)"}


def _build_kp(p):
    k = p["kp"]
    check_range(k["kp"], 0, 9.01, "Kp")
    if len(k) < 40:
        raise ValidationError(f"For få Kp-verdier: {len(k)}")
    k = k[k["time"] >= k["time"].max() - pd.Timedelta(days=30)]
    files = {
        "kp_recent.json": {
            "origin": p["origin"],
            "time": [x.strftime("%Y-%m-%dT%H:%M") for x in k["time"]],
            "kp": r(k["kp"], 2),
        }
    }
    return files, {"rows": len(k), "last_point": k["time"].iloc[-1].strftime("%Y-%m-%dT%H:%M")}


SOURCES = [
    Source(
        id="swpc_cycle",
        name="NOAA SWPC: observerte solsyklusindekser, F10.7 (månedlig) og prognose for syklus 25",
        provider="NOAA Space Weather Prediction Center",
        group="daily",
        urls=[f"{SWPC}/json/solar-cycle/observed-solar-cycle-indices.json", f"{SWPC}/json/solar-cycle/predicted-solar-cycle.json"],
        homepage="https://www.swpc.noaa.gov/products/solar-cycle-progression",
        license=SWPC_LICENSE,
        citation=SWPC_CITE,
        frequency="Oppdateres månedlig av NOAA; hentes daglig.",
        caveats="Prognosen revideres jevnlig og er en statistisk/empirisk modell, ikke en fysisk forutsigelse. SWPC bruker egen solflekkskala ved siden av SILSO.",
        fetch=_fetch_cycle,
        parse=_parse_cycle,
        build=_build_cycle,
    ),
    Source(
        id="swpc_recent",
        name="NOAA SWPC: daglig F10.7 og SESC-solflekktall, siste 30 dager",
        provider="NOAA Space Weather Prediction Center",
        group="daily",
        urls=[f"{SWPC}/text/daily-solar-indices.txt"],
        homepage="https://www.swpc.noaa.gov/products/solar-and-geophysical-event-reports",
        license=SWPC_LICENSE,
        citation=SWPC_CITE,
        frequency="Daglig.",
        caveats="F10.7 er målt ved Penticton/Dominion Radio Astrophysical Observatory (Canada) og rapportert av NOAA. SESC-solflekktallet er en rask, foreløpig tellemetode og avviker fra SILSO.",
        fetch=_fetch_recent,
        parse=_parse_recent,
        build=_build_recent,
        rolling=True,
    ),
    Source(
        id="kp_recent",
        name="Planetarisk Kp-indeks, siste 30 dager (GFZ Potsdam, reserve: NOAA SWPC)",
        provider="GFZ Helmholtz Centre for Geosciences, Potsdam",
        group="daily",
        urls=[GFZ_NOW, f"{SWPC}/products/noaa-planetary-k-index.json"],
        homepage="https://kp.gfz-potsdam.de/en/",
        license="CC BY 4.0",
        citation=(
            "Matzka, J., Stolle, C., Yamazaki, Y., Bronkalla, O. & Morschhauser, A. (2021), The geomagnetic Kp index and derived "
            "indices of geomagnetic activity, Space Weather 19, e2020SW002641. https://doi.org/10.1029/2020SW002641"
        ),
        frequency="Nowcast-verdier hver 3. time; endelige verdier senere.",
        caveats="Nowcast-Kp kan avvike litt fra endelig Kp. Fallback fra NOAA gir bare 7 dager.",
        fetch=_fetch_kp,
        parse=_parse_kp,
        build=_build_kp,
        rolling=True,
        fallback_note="NOAA SWPC planetary K-index brukes hvis GFZ ikke svarer.",
    ),
]
