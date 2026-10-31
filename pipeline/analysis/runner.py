"""Kjører alle analyser og skriver analysis_*.json + cycles.json. Én analyse som feiler stopper ikke de andre."""

from __future__ import annotations

import logging

from ..core import DATA_DIR, now_iso, write_json
from . import context, solar_earth, volcano
from .cycles import build_cycles, summarize
from .data import monthly_ssn

log = logging.getLogger("pipeline.analysis")


def run_analyses(manifest: dict, outdir=DATA_DIR) -> dict:
    status: dict = {}
    try:
        m = monthly_ssn(outdir)
        cycles = build_cycles(m["t"], m["smoothed"])
        if len(cycles) < 24:
            raise ValueError(f"Fant bare {len(cycles)} sykluser (forventet ≥ 25)")
        write_json("cycles.json", {"summary": summarize(cycles), "cycles": cycles, "method": "Minima i 13-måneders glattet månedlig solflekktall (SILSO V2.0); syklus 1 = minimum rundt 1755."}, outdir)
        status["cycles"] = {"status": "ok", "n_cycles": len(cycles), "n_tests": 0}
    except Exception as e:  # noqa: BLE001
        log.error("Syklusdeteksjon feilet: %s", e)
        status["cycles"] = {"status": "failed", "error": str(e)[:300]}
        manifest["analyses"] = status
        return status

    jobs = {
        "tsi": lambda: solar_earth.analyse_tsi(cycles, outdir),
        "temperature": lambda: solar_earth.analyse_temperature(outdir),
        "cosmic": lambda: solar_earth.analyse_cosmic(outdir),
        "geomag": lambda: solar_earth.analyse_geomag(cycles, outdir),
        "regional": lambda: solar_earth.analyse_regional(outdir),
        "volcano": lambda: volcano.analyse_volcano(cycles, outdir),
        "maunder": lambda: context.analyse_maunder(outdir),
        "spurious": lambda: context.analyse_spurious(outdir),
    }
    prev = manifest.get("analyses", {})
    for name, fn in jobs.items():
        try:
            res = fn()
            changed = write_json(f"analysis_{name}.json", res, outdir)
            old = prev.get(name, {})
            status[name] = {
                "status": "ok",
                "n_tests": res.get("n_tests"),
                "run_at": now_iso() if (changed or not old.get("run_at")) else old["run_at"],
                "error": None,
            }
            log.info("analyse %s: OK (n_tests=%s, endret=%s)", name, res.get("n_tests"), changed)
        except Exception as e:  # noqa: BLE001
            log.error("analyse %s FEILET: %s", name, e, exc_info=True)
            old = prev.get(name, {})
            status[name] = {"status": "stale" if old else "failed", "n_tests": old.get("n_tests"), "run_at": old.get("run_at"), "error": f"{type(e).__name__}: {e}"[:300]}
    manifest["analyses"] = status
    return status
