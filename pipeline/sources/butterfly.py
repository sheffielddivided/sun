"""Sommerfugldiagram: Royal Observatory Greenwich + USAF/NOAA solflekkarealer etter breddegrad (David Hathaway, NASA MSFC).

Verifisert 2026-10-31: https://solarscience.msfc.nasa.gov/greenwch/bflydata.txt (≈0,5 MB)
Format (se Hathaway): per Carrington-rotasjon én linje med rotasjonsnummeret, deretter fem linjer med 10 verdier
= 50 breddebiner jevnt fordelt i sin(bredde) fra -1 til +1; enhet: millionedeler av en halvkule.
Rotasjon 1 begynte 1853-11-09 (Carrington), gjennomsnittlig rotasjonstid 27,2753 døgn.
"""

from __future__ import annotations

import re
from datetime import date, timedelta

import numpy as np

from ..core import Source, ValidationError, ensure_not_html, http_get

URL = "https://solarscience.msfc.nasa.gov/greenwch/bflydata.txt"
CARRINGTON_EPOCH = date(1853, 11, 9)
SYNODIC = 27.2753
NBINS = 50


def rotation_to_decimal_year(n: int) -> float:
    d = CARRINGTON_EPOCH + timedelta(days=(n - 1 + 0.5) * SYNODIC)
    start = date(d.year, 1, 1)
    return d.year + (d - start).days / (366 if d.year % 4 == 0 else 365)


def parse_bfly(raw: bytes) -> tuple[np.ndarray, np.ndarray]:
    """Returnerer (rotasjonsnummer[n], areal[n, 50]) der bin 0 er sørligste bredde (-90°) og bin 49 nordligst."""
    toks = [t for t in re.split(r"[\s,]+", raw.decode("utf-8", errors="replace")) if t]
    vals = []
    for t in toks:
        try:
            vals.append(int(float(t)))
        except ValueError as e:
            raise ValidationError(f"Ugyldig token i bflydata: {t!r}") from e
    block = NBINS + 1
    if len(vals) < block * 100 or len(vals) % block != 0:
        raise ValidationError(f"bflydata: uventet antall verdier ({len(vals)}), ikke multiplum av {block}")
    arr = np.asarray(vals, dtype=float).reshape(-1, block)
    rot, area = arr[:, 0].astype(int), arr[:, 1:]
    if not (np.diff(rot) == 1).all():
        raise ValidationError("Rotasjonsnumre er ikke sammenhengende")
    return rot, area


def _fetch():
    return {"bfly": ensure_not_html(http_get(URL), "bflydata.txt")}


def _parse(raw):
    rot, area = parse_bfly(raw["bfly"])
    return {"rot": rot, "area": area}


def _build(p):
    rot, area = p["rot"], p["area"]
    if area.min() < 0 or area.max() > 1_000_000:
        raise ValidationError("Areal utenfor plausibelt område")
    if len(rot) < 1800:
        raise ValidationError(f"For få rotasjoner: {len(rot)}")
    # Hold fila kompakt: heltall, flat liste radvis (rotasjon × bredde)
    files = {
        "butterfly.json": {
            "rotation_start": int(rot[0]),
            "t0": round(rotation_to_decimal_year(int(rot[0])), 3),
            "dt": round(SYNODIC / 365.2425, 5),
            "nlat": NBINS,
            "unit": "millionedeler av en halvkule per breddebin (jevnt fordelt i sin(bredde))",
            "area": area.astype(int).ravel().tolist(),
        }
    }
    return files, {"rows": len(rot), "last_point": f"{rotation_to_decimal_year(int(rot[-1])):.2f}"}


SOURCE = Source(
    id="butterfly",
    name="Sommerfugldiagram: solflekkareal etter breddegrad (Greenwich/USAF/NOAA)",
    provider="NASA Marshall Space Flight Center (D. Hathaway) – data fra Royal Observatory Greenwich og USAF/NOAA",
    group="yearly",
    urls=[URL],
    homepage="https://solarscience.msfc.nasa.gov/greenwch.shtml",
    license="Åpne data fra NASA; oppgi kilde (Hathaway).",
    citation="Hathaway, D.H. (2015), The Solar Cycle, Living Reviews in Solar Physics 12, 4; data: https://solarscience.msfc.nasa.gov/greenwch.shtml",
    frequency="Oppdateres av Hathaway; hentes årlig.",
    caveats="Arealene etter 1976 (USAF/NOAA) er skalert med 1,4 av Hathaway for å tilsvare Greenwich. Datoer er omregnet fra Carrington-rotasjonsnummer.",
    fetch=_fetch,
    parse=_parse,
    build=_build,
)
