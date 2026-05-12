from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class EngineeringContext:
    solver: str
    material: str
    stress_summary: dict[str, float]
    safety_factor: float


class AiProvider(Protocol):
    def recommend(self, context: EngineeringContext) -> list[str]:
        ...


class LocalPlaceholderProvider:
    def recommend(self, context: EngineeringContext) -> list[str]:
        return [
            f"Review {context.solver} assumptions against load stationarity.",
            "Validate material SN parameters before design release.",
        ]


def sanitize_context(context: EngineeringContext) -> dict:
    return {
        "solver": context.solver,
        "material_family": context.material,
        "stress_summary": context.stress_summary,
        "safety_factor": context.safety_factor,
    }
