"""Kosmisk stråling: Oulu-gruppens modulasjonspotensial Φ (rekonstruert fra bakkebaserte nøytronmonitorer).

Direkte spørring mot Oulu NM-databasen (https://cosmicrays.oulu.fi/webform/onlinequery.cgi) returnerte
HTTP 500 for alle gyldige parametre ved test 2026-10-31, og NMDB (nest.nmdb.eu) krever autentisering (401).
Derfor brukes Oulus publiserte Φ-tabell (Usoskin et al.), som er avledet fra nøytronmonitorer
(inkl. Oulu) og dekker 1936–siste fullførte år:
  https://cosmicrays.oulu.fi/phi/Phi_mon.txt
Φ er omvendt relatert til kosmisk strålingsintensitet: høy Φ = sterk skjerming = lav kosmisk stråling.
"""

from __future__ import annotations

import re

import numpy as np
import pandas as pd

from ..core import Source, ValidationError, check_range, ensure_not_html, http_get, r

URL = "https://cosmicrays.oulu.fi/phi/Phi_mon.txt"


def parse_phi(raw: bytes) -> pd.DataFrame:
    rows = []
    for line in raw.decode("utf-8", errors="replace").splitlines():
        parts = line.split()
        if len(parts) == 14 and re.fullmatch(r"\d{4}", parts[0]):
            year = int(parts[0])
            for m, tok in enumerate(parts[1:13], start=1):
                if re.fullmatch(r"\d+(\.\d+)?", tok):
                    rows.append((year, m, year + (m - 0.5) / 12, float(tok)))
    if not rows:
        raise ValidationError("Phi_mon.txt: ingen datalinjer gjenkjent")
    return pd.DataFrame(rows, columns=["year", "month", "t", "phi"])


def _fetch():
    return {"phi": ensure_not_html(http_get(URL), "Phi_mon.txt")}


def _parse(raw):
    return {"phi": parse_phi(raw["phi"])}


def _build(p):
    d = p["phi"]
    check_range(d["phi"], 50, 2500, "Φ (MV)")
    if len(d) < 800:
        raise ValidationError(f"For få Φ-verdier: {len(d)}")
    files = {"cosmic_phi_monthly.json": {"t": r(d["t"], 3), "phi": r(d["phi"], 0)}}
    last = d.iloc[-1]
    return files, {"rows": len(d), "last_point": f"{int(last['year'])}-{int(last['month']):02d}"}


SOURCE = Source(
    id="cosmic",
    name="Modulasjonspotensial Φ for kosmisk stråling (Oulu, fra nøytronmonitorer), 1936–",
    provider="Cosmic Ray Station of the University of Oulu / Sodankylä Geophysical Observatory",
    group="monthly",
    urls=[URL],
    homepage="https://cosmicrays.oulu.fi/phi/phi.html",
    license="Kun forskning/utdanning og ikke-kommersielle offentlige tjenester; Oulu-stasjonen og Sodankylä Geophysical Observatory skal oppgis (se https://cosmicrays.oulu.fi/readme.html).",
    citation=(
        "Usoskin, I.G., Bazilevskaya, G.A. & Kovaltsov, G.A. (2011), Solar modulation parameter for cosmic rays since 1936 reconstructed "
        "from ground-based neutron monitors and ionization chambers, J. Geophys. Res. 116, A02104; data: Cosmic Ray Station of the "
        "University of Oulu / Sodankylä Geophysical Observatory."
    ),
    frequency="Oppdateres sjelden (årlig); hentes månedlig.",
    caveats=(
        "Φ er en modellparameter avledet fra nøytronmonitorer, ikke selve tellerater. Seriene ligger ofte ett år eller mer bak. "
        "Oulus direkte spørretjeneste for råtellerater var ikke tilgjengelig ved bygging (HTTP 500)."
    ),
    fetch=_fetch,
    parse=_parse,
    build=_build,
    fallback_note="Oulu NM-spørretjeneste ga HTTP 500; NMDB krever innlogging. Φ-tabellen fra Oulu brukes i stedet.",
)
