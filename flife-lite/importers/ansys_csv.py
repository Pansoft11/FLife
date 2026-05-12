from __future__ import annotations

import csv
from pathlib import Path

from .base import ImportValidationError, ParsedStressData, normalize_stress_to_mpa


class AnsysCsvImporter:
    name = "ANSYS CSV"

    def can_parse(self, path: Path) -> bool:
        return path.suffix.lower() == ".csv"

    def parse(self, path: Path) -> ParsedStressData:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            rows = list(csv.DictReader(handle))
        if not rows:
            raise ImportValidationError("ANSYS CSV contains no rows.")
        time_key = _find_key(rows[0], ["time", "time_s", "seconds"])
        stress_key = _find_key(rows[0], ["stress", "stress_mpa", "equivalent stress", "von-mises"])
        unit = "MPa" if "mpa" in stress_key.lower() else "Pa"
        return ParsedStressData(
            source=str(path),
            unit="MPa",
            time_s=[float(row[time_key]) for row in rows],
            stress_mpa=normalize_stress_to_mpa([float(row[stress_key]) for row in rows], unit),
            metadata={"importer": self.name},
        )


def _find_key(row: dict[str, str], candidates: list[str]) -> str:
    lowered = {key.lower(): key for key in row.keys()}
    for candidate in candidates:
        for lower, original in lowered.items():
            if candidate in lower:
                return original
    raise ImportValidationError(f"Missing required column: {candidates[0]}")
