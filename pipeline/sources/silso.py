"""SILSO / Royal Observatory of Belgium: solflekktall V2.0, gruppesolflekktall og hemisfæriske data.

Verifiserte URL-er (hentet 2026-10-31):
  https://www.sidc.be/silso/DATA/SN_m_tot_V2.0.csv     månedlig
  https://www.sidc.be/silso/DATA/SN_ms_tot_V2.0.csv    glattet månedlig (13 mnd)
  https://www.sidc.be/silso/DATA/SN_y_tot_V2.0.csv     årlig
  https://www.sidc.be/silso/DATA/SN_d_tot_V2.0.csv     daglig
  https://www.sidc.be/silso/DATA/SN_m_hem_V2.0.csv     månedlig, hemisfærer
  https://www.sidc.be/silso/DATA/EISN/EISN_current.csv nær sanntid (estimert internasjonalt solflekktall)
  https://www.sidc.be/SILSO/DATA/GroupNumber/GNbb2_y.txt, GNhs_y.txt  gruppesolflekktall
(De eldre /SILSO/INFO/snchrono/-URL-ene gir nå 404 – bare /silso/DATA/ brukes.)
"""

from __future__ import annotations

import io

import numpy as np
import pandas as pd

from ..core import Source, ValidationError, check_range, ensure_not_html, http_get, r

BASE = "https://www.sidc.be/silso/DATA"
GN = "https://www.sidc.be/SILSO/DATA/GroupNumber"

CITATION = (
    "SILSO World Data Center / Royal Observatory of Belgium, Brussels: «Sunspot Number and Long-term Solar "
    "Observations», Version 2.0. https://www.sidc.be/SILSO/"
)
LICENSE = "CC BY-NC 4.0 (SILSO). Krever kildehenvisning; ikke-kommersiell bruk."


def _csv(raw: bytes, ncols_min: int) -> pd.DataFrame:
    txt = raw.decode("utf-8", errors="replace")
    df = pd.read_csv(io.StringIO(txt), sep=";", header=None, skipinitialspace=True, comment="#")
    if df.shape[1] < ncols_min:
        raise ValidationError(f"Forventet minst {ncols_min} kolonner, fikk {df.shape[1]}")
    return df


def parse_monthly(raw: bytes) -> pd.DataFrame:
    """Format: år;måned;desimalår;verdi;std;antall obs;definitiv-flagg. -1 = mangler."""
    df = _csv(raw, 7).iloc[:, :7]
    df.columns = ["year", "month", "t", "ssn", "std", "nobs", "definitive"]
    df = df.apply(pd.to_numeric, errors="coerce").dropna(subset=["year", "month", "t"])
    df["ssn"] = df["ssn"].where(df["ssn"] >= 0)
    df["std"] = df["std"].where(df["std"] >= 0)
    df[["year", "month"]] = df[["year", "month"]].astype(int)
    return df.reset_index(drop=True)


def parse_yearly(raw: bytes) -> pd.DataFrame:
    """Format: desimalår (midt i året);verdi;std;antall obs;definitiv."""
    df = _csv(raw, 5).iloc[:, :5]
    df.columns = ["t", "ssn", "std", "nobs", "definitive"]
    df = df.apply(pd.to_numeric, errors="coerce").dropna(subset=["t"])
    df["ssn"] = df["ssn"].where(df["ssn"] >= 0)
    df["year"] = np.floor(df["t"]).astype(int)
    return df.reset_index(drop=True)


def parse_daily(raw: bytes) -> pd.DataFrame:
    """Format: år;mnd;dag;desimalår;verdi;std;antall obs;definitiv. -1 = mangler."""
    df = _csv(raw, 8).iloc[:, :8]
    df.columns = ["year", "month", "day", "t", "ssn", "std", "nobs", "definitive"]
    df = df.apply(pd.to_numeric, errors="coerce").dropna(subset=["year", "month", "day"])
    df["ssn"] = df["ssn"].where(df["ssn"] >= 0)
    df[["year", "month", "day"]] = df[["year", "month", "day"]].astype(int)
    df["date"] = pd.to_datetime(df[["year", "month", "day"]])
    return df.reset_index(drop=True)


def parse_hem_monthly(raw: bytes) -> pd.DataFrame:
    """Format: år;mnd;desimalår;total;nord;sør;std total;std nord;std sør;nobs ..."""
    df = _csv(raw, 6).iloc[:, :6]
    df.columns = ["year", "month", "t", "total", "north", "south"]
    df = df.apply(pd.to_numeric, errors="coerce").dropna(subset=["year", "month"])
    for c in ("total", "north", "south"):
        df[c] = df[c].where(df[c] >= 0)
    df[["year", "month"]] = df[["year", "month"]].astype(int)
    return df.reset_index(drop=True)


def parse_eisn(raw: bytes) -> pd.DataFrame:
    """Format: år, mnd, dag, desimalår, EISN, std, nstasjoner, nstasjoner2 (komma-separert)."""
    txt = raw.decode("utf-8", errors="replace")
    df = pd.read_csv(io.StringIO(txt), sep=",", header=None, skipinitialspace=True, comment="#", usecols=range(7))
    df.columns = ["year", "month", "day", "t", "ssn", "std", "nstations"]
    df = df.apply(pd.to_numeric, errors="coerce").dropna(subset=["year", "month", "day"])
    df["ssn"] = df["ssn"].where(df["ssn"] >= 0)
    df[["year", "month", "day"]] = df[["year", "month", "day"]].astype(int)
    df["date"] = pd.to_datetime(df[["year", "month", "day"]])
    return df.reset_index(drop=True)


def parse_group_yearly(raw: bytes) -> pd.DataFrame:
    """Whitespace-separert: år (midt); Gn; feil; ... -1 = mangler."""
    txt = raw.decode("utf-8", errors="replace")
    df = pd.read_csv(io.StringIO(txt), sep=r"\s+", header=None, comment="#", engine="python")
    df = df.iloc[:, :3]
    df.columns = ["t", "gn", "err"]
    df = df.apply(pd.to_numeric, errors="coerce").dropna(subset=["t"])
    df["gn"] = df["gn"].where(df["gn"] >= 0)
    df["err"] = df["err"].where(df["err"] >= 0)
    df["year"] = np.floor(df["t"]).astype(int)
    return df.reset_index(drop=True)


# ---------------------------------------------------------------------------
# Månedlige serier
# ---------------------------------------------------------------------------
def _fetch_monthly() -> dict[str, bytes]:
    out = {}
    for key, fn in {
        "monthly": "SN_m_tot_V2.0.csv",
        "smoothed": "SN_ms_tot_V2.0.csv",
        "yearly": "SN_y_tot_V2.0.csv",
        "hem": "SN_m_hem_V2.0.csv",
    }.items():
        out[key] = ensure_not_html(http_get(f"{BASE}/{fn}"), fn)
    return out


def _parse_monthly(raw):
    return {
        "monthly": parse_monthly(raw["monthly"]),
        "smoothed": parse_monthly(raw["smoothed"]),
        "yearly": parse_yearly(raw["yearly"]),
        "hem": parse_hem_monthly(raw["hem"]),
    }


def _build_monthly(p):
    m, s, y, h = p["monthly"], p["smoothed"], p["yearly"], p["hem"]
    check_range(m["ssn"], 0, 500, "Månedlig solflekktall")
    check_range(y["ssn"], 0, 400, "Årlig solflekktall")
    if len(m) < 3000:
        raise ValidationError(f"For få månedsverdier: {len(m)}")
    if m["year"].min() != 1749:
        raise ValidationError("Månedlig serie skal starte i 1749")
    merged = m.merge(s[["year", "month", "ssn"]].rename(columns={"ssn": "smoothed"}), on=["year", "month"], how="left")
    files = {
        "ssn_monthly.json": {
            "t": r(merged["t"], 3),
            "ssn": r(merged["ssn"], 1),
            "smoothed": r(merged["smoothed"], 1),
            "definitive": [int(v) for v in merged["definitive"].fillna(0)],
        },
        "ssn_yearly.json": {
            "year": [int(v) for v in y["year"]],
            "ssn": r(y["ssn"], 1),
            "std": r(y["std"], 1),
            "definitive": [int(v) for v in y["definitive"].fillna(0)],
        },
        "ssn_hemispheric_monthly.json": {
            "t": r(h["t"], 3),
            "north": r(h["north"], 1),
            "south": r(h["south"], 1),
        },
    }
    last = merged.dropna(subset=["ssn"]).iloc[-1]
    return files, {"rows": len(merged), "last_point": f"{int(last['year'])}-{int(last['month']):02d}"}


# ---------------------------------------------------------------------------
# Daglige serier
# ---------------------------------------------------------------------------
def _fetch_daily():
    return {
        "daily": ensure_not_html(http_get(f"{BASE}/SN_d_tot_V2.0.csv"), "SN_d_tot_V2.0.csv"),
        "eisn": ensure_not_html(http_get(f"{BASE}/EISN/EISN_current.csv"), "EISN_current.csv"),
    }


def _parse_daily(raw):
    return {"daily": parse_daily(raw["daily"]), "eisn": parse_eisn(raw["eisn"])}


def _build_daily(p):
    d, e = p["daily"], p["eisn"]
    check_range(d["ssn"], 0, 600, "Daglig solflekktall")
    if len(d) < 70000:
        raise ValidationError(f"For få daglige verdier: {len(d)}")
    recent = d[d["date"] >= d["date"].max() - pd.Timedelta(days=799)]
    files = {
        "ssn_daily_recent.json": {
            "date": [x.strftime("%Y-%m-%d") for x in recent["date"]],
            "ssn": r(recent["ssn"], 0),
            "eisn_date": [x.strftime("%Y-%m-%d") for x in e["date"]],
            "eisn": r(e["ssn"], 0),
        }
    }
    last = d.dropna(subset=["ssn"]).iloc[-1]["date"].strftime("%Y-%m-%d")
    return files, {"rows": len(d), "last_point": last}


# ---------------------------------------------------------------------------
# Gruppesolflekktall
# ---------------------------------------------------------------------------
def _fetch_groups():
    return {
        "backbone": ensure_not_html(http_get(f"{GN}/GNbb2_y.txt"), "GNbb2_y.txt"),
        "hs": ensure_not_html(http_get(f"{GN}/GNhs_y.txt"), "GNhs_y.txt"),
    }


def _parse_groups(raw):
    return {"backbone": parse_group_yearly(raw["backbone"]), "hs": parse_group_yearly(raw["hs"])}


def _build_groups(p):
    bb, hs = p["backbone"], p["hs"]
    check_range(bb["gn"], 0, 20, "Gruppetall (backbone)")
    check_range(hs["gn"], 0, 20, "Gruppetall (Hoyt & Schatten)")
    if bb["year"].min() > 1620:
        raise ValidationError("Gruppetall skal starte rundt 1610")
    merged = bb.merge(hs[["year", "gn", "err"]], on="year", how="outer", suffixes=("_bb", "_hs")).sort_values("year")
    files = {
        "group_yearly.json": {
            "year": [int(v) for v in merged["year"]],
            "backbone": r(merged["gn_bb"], 3),
            "backbone_err": r(merged["err_bb"], 3),
            "hs": r(merged["gn_hs"], 3),
        }
    }
    return files, {"rows": len(merged), "last_point": str(int(merged["year"].max()))}


SOURCES = [
    Source(
        id="silso_monthly",
        name="SILSO: månedlig, glattet og årlig solflekktall (V2.0) + hemisfæriske verdier",
        provider="SILSO / Royal Observatory of Belgium",
        group="monthly",
        urls=[f"{BASE}/SN_m_tot_V2.0.csv", f"{BASE}/SN_ms_tot_V2.0.csv", f"{BASE}/SN_y_tot_V2.0.csv", f"{BASE}/SN_m_hem_V2.0.csv"],
        homepage="https://www.sidc.be/SILSO/datafiles",
        license=LICENSE,
        citation=CITATION,
        frequency="Månedlig (første dagene i måneden); foreløpige verdier revideres.",
        caveats="Siste måneder er foreløpige. Før ca. 1849 er dekningen sparsom og usikkerheten stor. Hemisfæriske data finnes bare fra 1992.",
        fetch=_fetch_monthly,
        parse=_parse_monthly,
        build=_build_monthly,
    ),
    Source(
        id="silso_daily",
        name="SILSO: daglig solflekktall (V2.0) og nær-sanntids EISN",
        provider="SILSO / Royal Observatory of Belgium",
        group="daily",
        urls=[f"{BASE}/SN_d_tot_V2.0.csv", f"{BASE}/EISN/EISN_current.csv"],
        homepage="https://www.sidc.be/SILSO/datafiles",
        license=LICENSE,
        citation=CITATION,
        frequency="Daglig. V2.0-serien ligger typisk ca. én måned bak; EISN er et estimat i nær sanntid.",
        caveats="EISN er foreløpig og kan avvike fra den endelige verdien. Dagsverdier har stor spredning fra dag til dag.",
        fetch=_fetch_daily,
        parse=_parse_daily,
        build=_build_daily,
    ),
    Source(
        id="silso_groups",
        name="SILSO: gruppesolflekktall (backbone, Svalgaard & Schatten 2016; Hoyt & Schatten 1998)",
        provider="SILSO / Royal Observatory of Belgium (serier fra eksterne forfattere)",
        group="yearly",
        urls=[f"{GN}/GNbb2_y.txt", f"{GN}/GNhs_y.txt"],
        homepage="https://www.sidc.be/SILSO/groupnumber",
        license="Se SILSO sin side; serienes forfattere skal siteres.",
        citation=(
            "Svalgaard, L. & Schatten, K.H. (2016), Solar Physics 291, 2653–2684; "
            "Hoyt, D.V. & Schatten, K.H. (1998), Solar Physics 179, 189–219. Distribuert av SILSO."
        ),
        frequency="Statisk (historiske serier).",
        caveats="Forfatterne er uenige om langtidsnivået før 1880. Seriene er normalisert ulikt og kan ikke sammenlignes direkte med solflekktallet uten skalering.",
        fetch=_fetch_groups,
        parse=_parse_groups,
        build=_build_groups,
    ),
]
