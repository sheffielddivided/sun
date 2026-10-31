"""Kommandolinje: python -m pipeline.run --group daily|monthly|yearly|all [--analyses-only] [--only id,id]"""

from __future__ import annotations

import argparse
import logging
import sys

from .analysis.runner import run_analyses
from .core import DATA_DIR, load_manifest, run_source, save_manifest
from .sources import all_sources


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--group", choices=["daily", "monthly", "yearly", "all"], default="all")
    ap.add_argument("--analyses-only", action="store_true", help="Hopp over nedlasting; kjør bare analysene")
    ap.add_argument("--no-analyses", action="store_true", help="Hopp over analysene")
    ap.add_argument("--only", help="Kommaseparerte kilde-id-er")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if a.verbose else logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest()
    failed = []
    if not a.analyses_only:
        wanted = set(a.only.split(",")) if a.only else None
        for src in all_sources():
            if wanted and src.id not in wanted:
                continue
            if not wanted and src.group == "static":
                continue  # statiske kilder (avsluttede datasett) kjøres bare med --only
            if not wanted and a.group != "all" and src.group != a.group:
                continue
            entry = run_source(src, manifest)
            if entry["status"] != "ok":
                failed.append(src.id)
    run_ana = not a.no_analyses and (a.analyses_only or a.group in ("monthly", "yearly", "all"))
    if run_ana:
        run_analyses(manifest)
    save_manifest(manifest)
    if failed:
        logging.warning("Kilder med feil (siste gode versjon beholdt): %s", ", ".join(failed))
    return 0  # bygget skal aldri feile pga. én kilde


if __name__ == "__main__":
    sys.exit(main())
