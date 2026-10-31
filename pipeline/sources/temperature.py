"""Global temperatur: NASA GISTEMP v4 (primær) og HadCRUT5 (sekundær).

Verifiserte URL-er (2026-10-31):
  https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv   (anomali mot 1951–1980, «***» = mangler)
  https://www.metoffice.gov.uk/hadobs/hadcrut5/data/HadCRUT.5.0.2.0/analysis/diagnostics/
      HadCRUT.5.0.2.0.analysis.summary_series.global.monthly.csv     (anomali mot 1961–1990, med 95 % intervall)
Versjonsnummeret i HadCRUT-URL-en endres av og til; modulen prøver nyere versjoner først.
"""

from __future__ import annotations

import io

import pandas as pd

from ..core import Source, ValidationError, check_range, ensure_not_html, http_get, r

GISS = "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv"
HAD_BASE = "https://www.metoffice.gov.uk/hadobs/hadcrut5/data/{v}/analysis/diagnostics/{v}.analysis.summary_series.global.monthly.csv"
HAD_VERSIONS = ["HadCRUT.5.1.0.0", "HadCRUT.5.0.2.0", "HadCRUT.5.0.1.0"]
HAD_DEFAULT = HAD_BASE.format(v="HadCRUT.5.0.2.0")


def parse_gistemp(raw: bytes) -> pd.DataFrame:
    """Rad per år, kolonner Jan..Dec. Verdier skrevet som «.19»/«-.25»/«***». Returnerer månedlig lang tabell."""
    txt = raw.decode("utf-8", errors="replace")
    lines = txt.splitlines()
    start = next((i for i, ln in enumerate(lines) if ln.startswith("Year,")), None)
    if start is None:
        raise ValidationError("GISTEMP: fant ikke overskriftslinjen «Year,»")
    df = pd.read_csv(io.StringIO("\n".join(lines[start:])), na_values=["***", "****"])
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    if not set(months).issubset(df.columns):
        raise ValidationError("GISTEMP: månedskolonner mangler")
    df = df[pd.to_numeric(df["Year"], errors="coerce").notna()].copy()
    df["Year"] = df["Year"].astype(int)
    long = df.melt(id_vars="Year", value_vars=months, var_name="mon", value_name="anom")
    long["month"] = long["mon"].map({m: i + 1 for i, m in enumerate(months)})
    long["anom"] = pd.to_numeric(long["anom"], errors="coerce")
    long = long.rename(columns={"Year": "year"}).sort_values(["year", "month"]).dropna(subset=["anom"])
    long["t"] = long["year"] + (long["month"] - 0.5) / 12
    return long[["year", "month", "t", "anom"]].reset_index(drop=True)


def parse_hadcrut(raw: bytes) -> pd.DataFrame:
    df = pd.read_csv(io.StringIO(raw.decode("utf-8", errors="replace")))
    cols = list(df.columns)
    if not cols[0].lower().startswith("time"):
        raise ValidationError("HadCRUT5: første kolonne skal være Time")
    df = df.rename(columns={cols[0]: "time", cols[1]: "anom", cols[2]: "lo", cols[3]: "hi"})
    ym = df["time"].astype(str).str.extract(r"(\d{4})-(\d{2})")
    df["year"] = ym[0].astype(int)
    df["month"] = ym[1].astype(int)
    df["t"] = df["year"] + (df["month"] - 0.5) / 12
    return df[["year", "month", "t", "anom", "lo", "hi"]].dropna(subset=["anom"]).reset_index(drop=True)


def annual_mean(df: pd.DataFrame, col: str = "anom") -> pd.DataFrame:
    g = df.groupby("year").agg(v=(col, "mean"), n=(col, "size"))
    g = g[g["n"] == 12]
    return g["v"].reset_index().rename(columns={"v": col})


def rebase(df: pd.DataFrame, col: str, y0: int, y1: int) -> pd.DataFrame:
    base = df[(df["year"] >= y0) & (df["year"] <= y1)][col].mean()
    out = df.copy()
    out[col] = out[col] - base
    return out


def _fetch():
    giss = ensure_not_html(http_get(GISS), "GLB.Ts+dSST.csv")
    last = None
    for v in HAD_VERSIONS:
        try:
            had = ensure_not_html(http_get(HAD_BASE.format(v=v), retries=2), v)
            return {"gistemp": giss, "hadcrut": had, "had_version": v.encode()}
        except Exception as e:  # noqa: BLE001
            last = e
    raise ValidationError(f"HadCRUT5 utilgjengelig: {last}")


def _parse(raw):
    return {"gistemp": parse_gistemp(raw["gistemp"]), "hadcrut": parse_hadcrut(raw["hadcrut"]), "had_version": raw["had_version"].decode()}


def _build(p):
    g, h = p["gistemp"], p["hadcrut"]
    check_range(g["anom"], -1.0, 2.5, "GISTEMP-anomali")
    check_range(h["anom"], -1.5, 2.5, "HadCRUT5-anomali")
    if len(g) < 1500 or len(h) < 1900:
        raise ValidationError(f"For få månedsverdier: GISTEMP {len(g)}, HadCRUT5 {len(h)}")
    # felles referanseperiode 1961–1990 for sammenligning
    g61 = rebase(g, "anom", 1961, 1990)
    h61 = rebase(h, "anom", 1961, 1990)
    ga, ha = annual_mean(g61), annual_mean(h61)
    ann = ga.merge(ha, on="year", how="outer", suffixes=("_giss", "_had")).sort_values("year")
    files = {
        "temp_monthly.json": {
            "gistemp": {"t": r(g61["t"], 3), "anom": r(g61["anom"], 3)},
            "hadcrut5": {"t": r(h61["t"], 3), "anom": r(h61["anom"], 3), "lo": r(h61["lo"], 3), "hi": r(h61["hi"], 3)},
            "baseline": "1961–1990",
        },
        "temp_annual.json": {
            "year": [int(v) for v in ann["year"]],
            "gistemp": r(ann["anom_giss"], 3),
            "hadcrut5": r(ann["anom_had"], 3),
            "baseline": "1961–1990",
            "hadcrut_version": p["had_version"],
        },
    }
    last = g.iloc[-1]
    return files, {"rows": len(g) + len(h), "last_point": f"{int(last['year'])}-{int(last['month']):02d} (GISTEMP)"}


SOURCE = Source(
    id="temperature",
    name="Global middeltemperatur: NASA GISTEMP v4 og HadCRUT5",
    provider="NASA GISS; Met Office Hadley Centre / University of East Anglia CRU",
    group="monthly",
    urls=[GISS, HAD_DEFAULT],
    homepage="https://data.giss.nasa.gov/gistemp/",
    license="GISTEMP: åpne data, oppgi kilde. HadCRUT5: Open Government Licence v3.0, oppgi kilde.",
    citation=(
        "GISTEMP Team: GISS Surface Temperature Analysis (GISTEMP), version 4. NASA Goddard Institute for Space Studies, "
        "https://data.giss.nasa.gov/gistemp/; Lenssen, N. et al. (2019), J. Geophys. Res. Atmos. 124, 6307–6326. "
        "Morice, C.P. et al. (2021), An updated assessment of near-surface temperature change from 1850: the HadCRUT5 data set, "
        "J. Geophys. Res. Atmos. 126, e2019JD032361."
    ),
    frequency="Månedlig (midt i måneden). Hentes månedlig.",
    caveats="Dekningen er dårligere før ca. 1900 (særlig polarområder). GISTEMP bruker referanse 1951–1980 og HadCRUT5 1961–1990; her er begge omregnet til 1961–1990.",
    fetch=_fetch,
    parse=_parse,
    build=_build,
)
