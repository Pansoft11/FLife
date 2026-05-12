from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .materials import DEFAULT_MATERIALS


def seed_material_library(path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    materials = [
        *DEFAULT_MATERIALS.values(),
        {"name": "SAE 1045", "family": "SAE Steel", "uts_mpa": 625, "yield_mpa": 530, "sn_intercept": 9.5e18, "sn_slope": 5.8},
        {"name": "SAE 4140", "family": "SAE Steel", "uts_mpa": 1020, "yield_mpa": 655, "sn_intercept": 1.6e19, "sn_slope": 6.0},
        {"name": "Aluminum 6061-T6", "family": "Aluminum", "uts_mpa": 310, "yield_mpa": 276, "sn_intercept": 2.7e17, "sn_slope": 4.8},
        {"name": "Aluminum 2024-T3", "family": "Aluminum", "uts_mpa": 483, "yield_mpa": 345, "sn_intercept": 5.9e17, "sn_slope": 5.0},
        {"name": "Ti Grade 5", "family": "Titanium", "uts_mpa": 950, "yield_mpa": 880, "sn_intercept": 2.2e18, "sn_slope": 5.6},
    ]
    target.write_text(json.dumps({"version": "1.0", "materials": materials}, indent=2), encoding="utf-8")
    return target


def search_materials(path: str | Path, query: str = "", family: str | None = None) -> list[dict[str, Any]]:
    library = json.loads(Path(path).read_text(encoding="utf-8"))
    normalized = query.lower().strip()
    results = []
    for material in library["materials"]:
        matches_query = not normalized or normalized in material["name"].lower()
        matches_family = family is None or material["family"].lower() == family.lower()
        if matches_query and matches_family:
            results.append(material)
    return results
