"""Vulkanutbrudd (Smithsonian GVP, Holocene Eruptions) og vulkansk forcing (Gao et al. 2008, IVI2).

Smithsonian-nettsiden (volcano.si.edu/database/…) svarte 2026-10-31 med «site temporarily unavailable» (HTTP 403),
men GVPs åpne WFS-tjeneste (GeoServer) fungerer og leverer de samme Holocene-eruptions-dataene som GeoJSON:
  https://webservices.volcano.si.edu/geoserver/GVP-VOTW/wfs?service=WFS&version=1.0.0&request=GetFeature
      &typeName=GVP-VOTW:Smithsonian_VOTW_Holocene_Eruptions&outputFormat=application/json&cql_filter=…
IVI2 (NOAA NCEI paleo): https://www.ncei.noaa.gov/pub/data/paleo/climate_forcing/volcanic_aerosols/gao2008ivi2/
    IVI2TotalInjection_501-2000Version2.txt (global stratosfærisk sulfatinjeksjon, Tg)
"""

from __future__ import annotations

import json
import re

import numpy as np
import pandas as pd

from ..core import Source, ValidationError, check_range, ensure_not_html, http_get, r

WFS = "https://webservices.volcano.si.edu/geoserver/GVP-VOTW/wfs"
MIN_YEAR = 1500
MIN_VEI = 3
IVI2 = "https://www.ncei.noaa.gov/pub/data/paleo/climate_forcing/volcanic_aerosols/gao2008ivi2/IVI2TotalInjection_501-2000Version2.txt"


def _fetch_eruptions():
    params = {
        "service": "WFS",
        "version": "1.0.0",
        "request": "GetFeature",
        "typeName": "GVP-VOTW:Smithsonian_VOTW_Holocene_Eruptions",
        "outputFormat": "application/json",
        "cql_filter": f"ExplosivityIndexMax>={MIN_VEI} AND StartDateYear>={MIN_YEAR}",
    }
    return {"wfs": http_get(WFS, params=params, timeout=300)}


def parse_eruptions(raw: bytes) -> pd.DataFrame:
    obj = json.loads(raw)
    feats = obj.get("features")
    if not feats:
        raise ValidationError("GVP WFS: ingen features")
    rows = []
    for f in feats:
        p = f.get("properties", {})
        g = f.get("geometry") or {}
        lon, lat = (g.get("coordinates") or [None, None])[:2]
        rows.append(
            {
                "volcano": p.get("Volcano_Name"),
                "volcano_number": p.get("Volcano_Number"),
                "eruption_number": p.get("Eruption_Number"),
                "activity_type": p.get("Activity_Type"),
                "vei": p.get("ExplosivityIndexMax"),
                "vei_modifier": p.get("ExplosivityIndexModifier"),
                "year": p.get("StartDateYear"),
                "year_mod": p.get("StartDateYearModifier"),
                "year_unc": p.get("StartDateYearUncertainty"),
                "month": p.get("StartDateMonth"),
                "day": p.get("StartDateDay"),
                "day_unc": p.get("StartDateDayUncertainty"),
                "end_year": p.get("EndDateYear"),
                "lat": lat,
                "lon": lon,
            }
        )
    df = pd.DataFrame(rows)
    for c in ("vei", "year", "month", "day", "year_unc", "day_unc", "end_year"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["vei", "year"])
    df["year"] = df["year"].astype(int)
    df["vei"] = df["vei"].astype(int)
    df["month"] = df["month"].fillna(0).astype(int)
    df["day"] = df["day"].fillna(0).astype(int)
    # Tid som desimalår (midt i måneden); ukjent måned → midt i året
    df["t"] = np.where(df["month"] > 0, df["year"] + (df["month"] - 0.5) / 12, df["year"] + 0.5)
    # Presis startdato: liten usikkerhet og ikke en flerårig episode (f.eks. Tambora 1812–1815 er registrert med start 1812)
    dur = (df["end_year"] - df["year"]).fillna(0)
    df["precise"] = (df["year_unc"].fillna(0) == 0) & (df["day_unc"].fillna(0) < 30) & (dur < 1) & (df["month"] > 0)
    return df.sort_values(["year", "month", "eruption_number"]).reset_index(drop=True)


def _parse_eruptions(raw):
    return {"eruptions": parse_eruptions(raw["wfs"])}


def _build_eruptions(p):
    d = p["eruptions"]
    check_range(d["vei"], 0, 8, "VEI")
    check_range(d["year"], MIN_YEAR, 2100, "Utbruddsår")
    n4 = int((d["vei"] >= 4).sum())
    if n4 < 150:
        raise ValidationError(f"For få VEI≥4-utbrudd ({n4}); forventer ≳ 180")
    files = {
        "volcano_eruptions.json": {
            "min_vei": MIN_VEI,
            "min_year": MIN_YEAR,
            "volcano": list(d["volcano"]),
            "year": [int(v) for v in d["year"]],
            "month": [int(v) for v in d["month"]],
            "day": [int(v) for v in d["day"]],
            "t": r(d["t"], 3),
            "vei": [int(v) for v in d["vei"]],
            "vei_uncertain": [bool(v == "?") for v in d["vei_modifier"]],
            "confirmed": [bool(v == "Confirmed Eruption") for v in d["activity_type"]],
            "precise": [bool(v) for v in d["precise"]],
            "lat": r(d["lat"], 2),
            "lon": r(d["lon"], 2),
        }
    }
    last = d.iloc[-1]
    return files, {"rows": len(d), "last_point": f"{int(last['year'])} ({last['volcano']})"}


def parse_ivi2(raw: bytes) -> pd.DataFrame:
    rows = []
    for line in raw.decode("utf-8", errors="replace").splitlines():
        m = re.match(r"^\s*(\d{3,4})\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)", line)
        if m:
            rows.append((int(m[1]), float(m[2]), float(m[3]), float(m[4])))
    if not rows:
        raise ValidationError("IVI2: ingen datalinjer")
    return pd.DataFrame(rows, columns=["year", "nh", "sh", "global"])


def _fetch_ivi2():
    return {"ivi2": ensure_not_html(http_get(IVI2), "IVI2TotalInjection")}


def _parse_ivi2(raw):
    return {"ivi2": parse_ivi2(raw["ivi2"])}


def _build_ivi2(p):
    d = p["ivi2"]
    check_range(d["global"], 0, 300, "IVI2 global injeksjon (Tg)")
    if len(d) < 1400:
        raise ValidationError("IVI2 skal dekke 501–2000")
    d = d[d["year"] >= 1500]
    files = {"volcano_forcing_ivi2.json": {"year": [int(v) for v in d["year"]], "global_tg": r(d["global"], 2), "nh_tg": r(d["nh"], 2), "sh_tg": r(d["sh"], 2)}}
    return files, {"rows": len(d), "last_point": str(int(d["year"].max()))}


SOURCES = [
    Source(
        id="gvp_eruptions",
        name="Holocene-utbrudd med VEI ≥ 3 siden 1500 (Smithsonian Global Volcanism Program)",
        provider="Smithsonian Institution – Global Volcanism Program",
        group="yearly",
        urls=[WFS],
        homepage="https://volcano.si.edu/",
        license="Smithsonian Open Access / GVP: fritt tilgjengelig; kilden skal oppgis (se GVP sine retningslinjer).",
        citation="Global Volcanism Program, Smithsonian Institution: Volcanoes of the World (VOTW), Holocene Eruptions. https://volcano.si.edu/",
        frequency="Løpende redigert; hentes årlig.",
        caveats=(
            "Registreringen er ujevn: færre små og mellomstore utbrudd er dokumentert lenger tilbake i tid, særlig før ca. 1850 "
            "og i avsidesliggende områder. VEI er en grov logaritmisk skala for utbruddets størrelse, ikke for klimapåvirkning "
            "(svovelutslipp og breddegrad er viktigere). Start- og sluttdatoer kan være unøyaktige."
        ),
        fetch=_fetch_eruptions,
        parse=_parse_eruptions,
        build=_build_eruptions,
        fallback_note="Smithsonian-nettsiden var utilgjengelig; data hentes fra GVPs WFS-tjeneste (samme database).",
    ),
    Source(
        id="ivi2",
        name="Vulkansk stratosfærisk sulfatinjeksjon (IVI2), Gao, Robock & Ammann 2008",
        provider="NOAA NCEI Paleoclimatology (data fra Rutgers/Univ. of Michigan)",
        group="yearly",
        urls=[IVI2],
        homepage="https://www.ncei.noaa.gov/pub/data/paleo/climate_forcing/volcanic_aerosols/gao2008ivi2/",
        license="Åpne paleoklimadata (NOAA NCEI); oppgi kilde.",
        citation="Gao, C., Robock, A. & Ammann, C. (2008), Volcanic forcing of climate over the past 1500 years: An improved ice core-based index for climate models, J. Geophys. Res. 113, D23111.",
        frequency="Statisk (rekonstruksjon 501–2000).",
        caveats="Baserer på iskjerner (sulfat) og dateres med en usikkerhet på noen år; dekker ikke perioden etter 2000. NASA GISS sin stratosfæriske aerosol-fil (tau) var ikke tilgjengelig på den gamle URL-en.",
        fetch=_fetch_ivi2,
        parse=_parse_ivi2,
        build=_build_ivi2,
        fallback_note="GISS stratosfærisk aerosol-URL ga 404; IVI2 fra NOAA NCEI brukes.",
    ),
]
