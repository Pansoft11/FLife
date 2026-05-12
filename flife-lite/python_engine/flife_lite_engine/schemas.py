from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class MaterialInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = "steel-42crmo4"
    name: str = "42CrMo4 Steel"
    uts_mpa: float = Field(default=1080.0, gt=0, alias="utsMpa")
    sn_intercept: float = Field(default=1.8e19, gt=0, alias="snIntercept")
    sn_slope: float = Field(default=6.0, gt=0, alias="snSlope")


class AnalysisSettings(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    method: Literal["rainflow", "dirlik", "narrowband", "tovo-benasciutti"] = "dirlik"
    mean_stress_correction: Literal["none", "goodman"] = Field(default="goodman", alias="meanStressCorrection")
    cycle_counting: Literal["four-point", "three-point"] = Field(default="four-point", alias="cycleCounting")
    safety_factor: float = Field(default=1.2, gt=0, alias="safetyFactor")
    damage_model: Literal["miners-rule"] = Field(default="miners-rule", alias="damageModel")


class AnalysisRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    input_path: str | None = Field(default=None, alias="inputPath")
    time_column: str | None = Field(default=None, alias="timeColumn")
    stress_column: str | None = Field(default=None, alias="stressColumn")
    sampling_interval: float = Field(default=0.0005, gt=0, alias="samplingInterval")
    material: MaterialInput = MaterialInput()
    settings: AnalysisSettings = AnalysisSettings()


class CycleBin(BaseModel):
    range: float
    mean: float
    count: float


class SnPoint(BaseModel):
    cycles: float
    stress: float


class AnalysisResponse(BaseModel):
    life_seconds: float
    damage_per_second: float
    peak_stress_mpa: float
    rms_stress_mpa: float
    cycles: list[CycleBin]
    sn_curve: list[SnPoint]
    method: str
