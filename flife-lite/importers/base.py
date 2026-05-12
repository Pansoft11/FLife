from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


class ImportValidationError(ValueError):
    pass


@dataclass
class ParsedStressData:
    source: str
    unit: str
    time_s: list[float]
    stress_mpa: list[float]
    metadata: dict[str, str]


class StressImporter(Protocol):
    name: str

    def can_parse(self, path: Path) -> bool:
        ...

    def parse(self, path: Path) -> ParsedStressData:
        ...


def normalize_stress_to_mpa(values: list[float], unit: str) -> list[float]:
    normalized = unit.lower()
    if normalized == "mpa":
        return values
    if normalized == "pa":
        return [value / 1_000_000 for value in values]
    if normalized == "psi":
        return [value * 0.00689476 for value in values]
    raise ImportValidationError(f"Unsupported stress unit: {unit}")
