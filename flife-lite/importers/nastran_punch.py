from __future__ import annotations

from pathlib import Path

from .base import ImportValidationError, ParsedStressData


class NastranPunchImporter:
    name = "Nastran Punch"

    def can_parse(self, path: Path) -> bool:
        return path.suffix.lower() in {".pch", ".punch"}

    def parse(self, path: Path) -> ParsedStressData:
        values: list[float] = []
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            parts = line.split()
            for part in parts:
                try:
                    values.append(float(part))
                    break
                except ValueError:
                    continue
        if not values:
            raise ImportValidationError("No numeric stress values found in punch file.")
        return ParsedStressData(
            source=str(path),
            unit="MPa",
            time_s=list(range(len(values))),
            stress_mpa=values,
            metadata={"importer": self.name, "time_basis": "index"},
        )
