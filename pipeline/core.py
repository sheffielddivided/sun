"""Felles kjerne for datapipelinen: nedlasting, skriving, validering og manifest."""

from __future__ import annotations

import hashlib
import json
import logging
import math
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import requests

log = logging.getLogger("pipeline")

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "public" / "data"
MANIFEST_PATH = DATA_DIR / "manifest.json"
USER_AGENT = "sun-site-pipeline/1.0 (+https://github.com/sheffielddivided/sun; open-data research/education)"


class ValidationError(Exception):
    """Rådata ble hentet, men består ikke kvalitetskontrollen."""


# ---------------------------------------------------------------------------
# Nedlasting
# ---------------------------------------------------------------------------
def http_get(url: str, *, params: dict | None = None, retries: int = 4, timeout: int = 120) -> bytes:
    """Last ned en URL med eksponentiell backoff. Kaster ved vedvarende feil."""
    last: Exception | None = None
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, timeout=timeout, headers={"User-Agent": USER_AGENT})
            r.raise_for_status()
            if not r.content:
                raise ValidationError(f"Tomt svar fra {url}")
            return r.content
        except (requests.RequestException, ValidationError) as e:  # noqa: PERF203
            last = e
            wait = 2 ** (attempt + 1)
            log.warning("GET %s feilet (%s). Prøver igjen om %ss", url, e, wait)
            time.sleep(wait)
    raise ValidationError(f"Kunne ikke hente {url}: {last}")


def looks_like_html(raw: bytes) -> bool:
    head = raw[:400].lstrip().lower()
    return head.startswith(b"<!doctype html") or head.startswith(b"<html") or b"<title>404" in head


def ensure_not_html(raw: bytes, url: str) -> bytes:
    if looks_like_html(raw):
        raise ValidationError(f"{url} returnerte HTML (feilside) i stedet for data")
    return raw


# ---------------------------------------------------------------------------
# Skriving
# ---------------------------------------------------------------------------
def _clean(o: Any) -> Any:
    if isinstance(o, dict):
        return {k: _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, np.ndarray):
        return [_clean(v) for v in o.tolist()]
    if isinstance(o, (np.floating, float)):
        f = float(o)
        return None if (math.isnan(f) or math.isinf(f)) else f
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    return o


def dumps(obj: Any) -> str:
    return json.dumps(_clean(obj), separators=(",", ":"), ensure_ascii=False, sort_keys=False)


def r(values, nd: int = 2):
    """Avrund en sekvens (NaN → None) for kompakt JSON."""
    arr = np.asarray(values, dtype=float)
    out = np.round(arr, nd)
    return [None if not np.isfinite(v) else (int(v) if nd == 0 else float(v)) for v in out]


def write_json(name: str, obj: Any, outdir: Path = DATA_DIR) -> bool:
    """Skriv JSON bare hvis innholdet har endret seg. Returnerer True ved endring."""
    outdir.mkdir(parents=True, exist_ok=True)
    path = outdir / name
    text = dumps(obj)
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def read_json(name: str, outdir: Path = DATA_DIR) -> Any:
    return json.loads((outdir / name).read_text(encoding="utf-8"))


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


# ---------------------------------------------------------------------------
# Kildebeskrivelse
# ---------------------------------------------------------------------------
@dataclass
class Source:
    id: str
    name: str
    provider: str
    group: str  # daily | monthly | yearly
    urls: list[str]
    homepage: str
    license: str
    citation: str
    frequency: str
    caveats: str
    fetch: Callable[[], dict[str, bytes]]
    parse: Callable[[dict[str, bytes]], dict[str, Any]]
    build: Callable[[dict[str, Any]], tuple[dict[str, Any], dict[str, Any]]]
    # (files, meta) der meta = {"rows": int, "last_point": str}
    rolling: bool = False  # True for «siste N dager»-serier (radantall kan ikke sammenlignes)
    fallback_note: str = ""
    extra: dict = field(default_factory=dict)


def load_manifest(path: Path = MANIFEST_PATH) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"schema": 1, "generated_at": None, "sources": {}, "analyses": {}}


def run_source(src: Source, manifest: dict, outdir: Path = DATA_DIR) -> dict:
    """Hent, parse, valider og skriv én kilde. Aldri kast: ved feil beholdes forrige versjon."""
    prev = manifest["sources"].get(src.id, {})
    entry = {
        "id": src.id,
        "name": src.name,
        "provider": src.provider,
        "group": src.group,
        "urls": src.urls,
        "homepage": src.homepage,
        "license": src.license,
        "citation": src.citation,
        "frequency": src.frequency,
        "caveats": src.caveats,
        "fallback_note": src.fallback_note,
    }
    try:
        raw = src.fetch()
        parsed = src.parse(raw)
        files, meta = src.build(parsed)
        if not files:
            raise ValidationError("Ingen utdatafiler produsert")
        rows = int(meta["rows"])
        if rows <= 0:
            raise ValidationError("Null rader etter parsing")
        prev_rows = prev.get("rows")
        if prev_rows and not src.rolling and rows < 0.9 * prev_rows:
            raise ValidationError(f"Radantall falt dramatisk: {prev_rows} → {rows}")
        changed = False
        for name, obj in files.items():
            changed |= write_json(name, obj, outdir)
        digest = hashlib.sha256("".join(dumps(files[k]) for k in sorted(files)).encode()).hexdigest()[:16]
        entry.update(
            status="ok",
            rows=rows,
            last_point=meta.get("last_point"),
            sha256=digest,
            files=sorted(files),
            fetched_at=now_iso() if (changed or not prev.get("fetched_at")) else prev["fetched_at"],
            error=None,
        )
        log.info("%s: OK (%s rader, siste punkt %s, endret=%s)", src.id, rows, meta.get("last_point"), changed)
    except Exception as e:  # noqa: BLE001 – bevisst bred: ingen kilde skal stoppe bygget
        log.error("%s: FEILET – %s", src.id, e)
        entry.update(
            status="stale" if prev.get("fetched_at") else "failed",
            rows=prev.get("rows"),
            last_point=prev.get("last_point"),
            sha256=prev.get("sha256"),
            files=prev.get("files", []),
            fetched_at=prev.get("fetched_at"),
            error=f"{type(e).__name__}: {e}"[:500],
            failed_at=now_iso(),
        )
    manifest["sources"][src.id] = entry
    return entry


def save_manifest(manifest: dict, path: Path = MANIFEST_PATH) -> bool:
    manifest["generated_at"] = manifest.get("generated_at")
    text = dumps(manifest)
    if path.exists():
        old = json.loads(path.read_text(encoding="utf-8"))
        cmp_new = json.loads(text)
        old.pop("generated_at", None)
        cmp_new.pop("generated_at", None)
        if old == cmp_new:
            return False
    manifest["generated_at"] = now_iso()
    path.write_text(dumps(manifest), encoding="utf-8")
    return True


# ---------------------------------------------------------------------------
# Hjelpere for validering
# ---------------------------------------------------------------------------
def check_range(s: pd.Series, lo: float, hi: float, what: str) -> None:
    s = s.dropna()
    if s.empty:
        raise ValidationError(f"{what}: ingen verdier")
    if s.min() < lo or s.max() > hi:
        raise ValidationError(f"{what}: verdier utenfor plausibelt område [{lo}, {hi}]: min={s.min()}, max={s.max()}")


def decimal_year(year: int, month: int, day: int = 15) -> float:
    return year + (month - 0.5) / 12 if day == 15 else year + (month - 1 + day / 31) / 12
