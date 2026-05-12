from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import FLife  # noqa: E402

from .schemas import AnalysisRequest, AnalysisResponse, CycleBin, SnPoint


def run_fatigue_analysis(payload: dict[str, Any] | AnalysisRequest) -> AnalysisResponse:
    request = payload if isinstance(payload, AnalysisRequest) else AnalysisRequest.model_validate(payload)
    stress = _load_stress_history(request)
    stress = stress - np.mean(stress)
    stress = stress / max(request.settings.safety_factor, 1e-9)

    spectral_data = FLife.SpectralData(
        input={"time_history": stress, "dt": request.sampling_interval},
        nperseg=min(1280, max(64, stress.size // 2)),
    )

    material = request.material
    method = request.settings.method
    if method == "rainflow":
      estimator = FLife.Rainflow(spectral_data)
      kwargs: dict[str, Any] = {"algorithm": request.settings.cycle_counting}
      if request.settings.mean_stress_correction == "goodman":
          kwargs["Su"] = material.uts_mpa
      life_seconds = estimator.get_life(C=material.sn_intercept, k=material.sn_slope, **kwargs)
    elif method == "narrowband":
      life_seconds = FLife.Narrowband(spectral_data).get_life(C=material.sn_intercept, k=material.sn_slope)
    elif method == "tovo-benasciutti":
      life_seconds = FLife.TovoBenasciutti(spectral_data).get_life(C=material.sn_intercept, k=material.sn_slope)
    else:
      life_seconds = FLife.Dirlik(spectral_data).get_life(C=material.sn_intercept, k=material.sn_slope)

    cycles = _cycle_bins(spectral_data, request.settings.cycle_counting)
    life_seconds = float(life_seconds)
    return AnalysisResponse(
        life_seconds=life_seconds,
        damage_per_second=float(1.0 / life_seconds) if life_seconds > 0 else math.inf,
        peak_stress_mpa=float(np.max(np.abs(stress))),
        rms_stress_mpa=float(np.sqrt(np.mean(np.square(stress)))),
        cycles=cycles,
        sn_curve=_sn_curve(material.sn_intercept, material.sn_slope),
        method=method,
    )


def _load_stress_history(request: AnalysisRequest) -> np.ndarray:
    if request.input_path:
        path = Path(request.input_path)
        if not path.exists():
            raise FileNotFoundError(f"Input file does not exist: {path}")
        data = _read_table(path)
        column = request.stress_column or _guess_stress_column(data)
        values = np.asarray(data[column], dtype=float)
    else:
        duration = 32.0
        t = np.arange(0, duration, request.sampling_interval)
        values = 62.0 * np.sin(2 * np.pi * 27 * t) + 28.0 * np.sin(2 * np.pi * 71 * t)
        values += 8.0 * np.sin(2 * np.pi * 123 * t)

    if values.ndim != 1 or values.size < 64:
        raise ValueError("Stress history must contain at least 64 numeric samples.")
    if not np.all(np.isfinite(values)):
        raise ValueError("Stress history contains non-finite values.")
    return values


def _read_table(path: Path) -> dict[str, list[float]]:
    suffix = path.suffix.lower()
    if suffix == ".xlsx":
        import pandas as pd

        frame = pd.read_excel(path)
        return frame.to_dict(orient="list")
    if suffix == ".csv":
        import pandas as pd

        row_count = sum(1 for _ in path.open("rb"))
        if row_count > 250_000:
            chunks = pd.read_csv(path, chunksize=100_000)
            frame = pd.concat(chunks, ignore_index=True)
        else:
            frame = pd.read_csv(path)
        return frame.to_dict(orient="list")

    raw = np.loadtxt(path)
    if raw.ndim == 1:
        return {"stress": raw.tolist()}
    return {f"col_{index}": raw[:, index].tolist() for index in range(raw.shape[1])}


def _guess_stress_column(data: dict[str, list[float]]) -> str:
    for name in data.keys():
        lowered = name.lower()
        if "stress" in lowered or lowered in {"s", "sigma", "mpa"}:
            return name
    numeric_columns = list(data.keys())
    if not numeric_columns:
        raise ValueError("No columns found in input file.")
    return numeric_columns[-1]


def _cycle_bins(spectral_data: Any, algorithm: str) -> list[CycleBin]:
    ranges, means, *rest = FLife.Rainflow(spectral_data)._get_cycles(algorithm=algorithm)
    counts = rest[0] if rest else np.ones_like(ranges)
    if ranges.size == 0:
        return []
    bins = np.linspace(float(np.min(ranges)), float(np.max(ranges)), 18)
    histogram, edges = np.histogram(ranges, bins=bins, weights=counts)
    mean_value = float(np.mean(means)) if means.size else 0.0
    return [
        CycleBin(range=float((edges[i] + edges[i + 1]) / 2), mean=mean_value, count=float(histogram[i]))
        for i in range(len(histogram))
        if histogram[i] > 0
    ]


def _sn_curve(intercept: float, slope: float) -> list[SnPoint]:
    cycles = np.logspace(3, 8, 40)
    return [SnPoint(cycles=float(n), stress=float((intercept / n) ** (1.0 / slope))) for n in cycles]
