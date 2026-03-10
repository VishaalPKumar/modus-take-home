from datetime import date, datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator


class Methodology(str, Enum):
    COMPS = "comps"
    DCF = "dcf"
    LAST_ROUND = "last_round"


class CompsInput(BaseModel):
    revenue: float = Field(gt=0, description="Annual revenue in USD")
    ebitda: float | None = Field(default=None, gt=0, description="Annual EBITDA in USD")


class DCFInput(BaseModel):
    revenue: float = Field(gt=0, description="Current annual revenue in USD")
    growth_rate: float = Field(default=0.15, ge=0, le=1, description="Annual revenue growth rate")
    discount_rate: float = Field(default=0.10, gt=0, le=1, description="WACC / discount rate")
    terminal_growth_rate: float = Field(default=0.03, ge=0, le=0.10, description="Terminal growth rate")
    projection_years: int = Field(default=5, ge=1, le=10, description="Number of years to project")
    profit_margin: float = Field(default=0.15, ge=-1, le=1, description="Net profit margin for FCF estimation")

    @model_validator(mode="after")
    def discount_must_exceed_terminal_growth(self) -> "DCFInput":
        if self.discount_rate <= self.terminal_growth_rate:
            raise ValueError(
                f"discount_rate ({self.discount_rate}) must be greater than "
                f"terminal_growth_rate ({self.terminal_growth_rate})"
            )
        return self


class LastRoundInput(BaseModel):
    post_money_valuation: float = Field(gt=0, description="Post-money valuation from last round in USD")
    round_date: date = Field(description="Date of last funding round")


class ValuationRequest(BaseModel):
    company_name: str = Field(min_length=1, description="Name of the portfolio company")
    sector: str = Field(min_length=1, description="Industry sector")
    methodologies: list[Methodology] = Field(min_length=1, description="Valuation methods to apply")
    comps_input: CompsInput | None = None
    dcf_input: DCFInput | None = None
    last_round_input: LastRoundInput | None = None

    @model_validator(mode="after")
    def inputs_match_methodologies(self) -> "ValuationRequest":
        method_to_field = {
            Methodology.COMPS: ("comps_input", self.comps_input),
            Methodology.DCF: ("dcf_input", self.dcf_input),
            Methodology.LAST_ROUND: ("last_round_input", self.last_round_input),
        }
        for method in self.methodologies:
            field_name, field_value = method_to_field[method]
            if field_value is None:
                raise ValueError(f"{field_name} is required when '{method.value}' is in methodologies")
        return self


class SensitivityRequest(BaseModel):
    methodology: Methodology
    sector: str | None = None
    comps_input: CompsInput | None = None
    dcf_input: DCFInput | None = None
    last_round_input: LastRoundInput | None = None

    @model_validator(mode="after")
    def input_matches_methodology(self) -> "SensitivityRequest":
        method_to_field = {
            Methodology.COMPS: ("comps_input", self.comps_input),
            Methodology.DCF: ("dcf_input", self.dcf_input),
            Methodology.LAST_ROUND: ("last_round_input", self.last_round_input),
        }
        field_name, field_value = method_to_field[self.methodology]
        if field_value is None:
            raise ValueError(f"{field_name} is required for methodology '{self.methodology.value}'")
        if self.methodology == Methodology.COMPS and not self.sector:
            raise ValueError("sector is required for methodology 'comps'")
        return self


class SensitivityPoint(BaseModel):
    parameters: dict[str, float]
    estimated_value: float


class SensitivityResponse(BaseModel):
    methodology: Methodology
    base_estimated_value: float
    varied_parameters: list[str]
    data_points: list[SensitivityPoint]


class ValuationStep(BaseModel):
    description: str
    detail: str


class ValuationResult(BaseModel):
    methodology: Methodology
    estimated_value: float
    value_range: tuple[float, float]
    assumptions: dict[str, Any]
    steps: list[ValuationStep]
    citations: list[str]


class ValuationReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    company_name: str
    sector: str
    results: list[ValuationResult]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
