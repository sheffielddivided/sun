"""Registeret over datakilder. Én modul per kilde; hver eksporterer `SOURCE`."""

from __future__ import annotations

from importlib import import_module

MODULES = [
    "silso",
    "swpc",
    "gfz_kp",
    "tsi",
    "temperature",
    "cosmic",
    "climate_indices",
    "volcanoes",
    "butterfly",
]


def all_sources():
    out = []
    for m in MODULES:
        mod = import_module(f"pipeline.sources.{m}")
        out.extend(getattr(mod, "SOURCES", None) or [mod.SOURCE])
    return out
