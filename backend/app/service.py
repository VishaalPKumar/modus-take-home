import logging

from app.constants import DCF_DISCOUNT_RATE_RANGE, DCF_GROWTH_RATE_RANGE, SENSITIVITY_STEPS
from app.data.provider import DataProvider
from app.engines.comps import CompsEngine
from app.engines.dcf import DCFEngine
from app.engines.last_round import LastRoundEngine
from app.models import (
    CompsInput,
    DCFInput,
    LastRoundInput,
    Methodology,
    SensitivityPoint,
    SensitivityRequest,
    SensitivityResponse,
    ValuationReport,
    ValuationRequest,
    ValuationResult,
)

logger = logging.getLogger(__name__)


class ValuationService:
    def __init__(self, data_provider: DataProvider):
        self.data_provider = data_provider
        self._engines = {
            Methodology.COMPS: CompsEngine(data_provider),
            Methodology.DCF: DCFEngine(),
            Methodology.LAST_ROUND: LastRoundEngine(data_provider),
        }

    def run(self, request: ValuationRequest) -> ValuationReport:
        methods = [m.value for m in request.methodologies]
        logger.info("Starting valuation for '%s' using %s", request.company_name, methods)

        results: list[ValuationResult] = []

        for method in request.methodologies:
            result = self._run_method(method, request)
            results.append(result)

        report = ValuationReport(
            company_name=request.company_name,
            sector=request.sector,
            results=results,
        )
        logger.info("Valuation complete — report %s", report.id)
        return report

    def sensitivity(self, request: SensitivityRequest) -> SensitivityResponse:
        if request.methodology == Methodology.DCF:
            return self._sensitivity_dcf(request.dcf_input)
        elif request.methodology == Methodology.COMPS:
            return self._sensitivity_comps(request.sector, request.comps_input)
        elif request.methodology == Methodology.LAST_ROUND:
            return self._sensitivity_last_round(request.last_round_input)
        else:
            raise ValueError(f"Unknown methodology: {request.methodology}")

    def _sensitivity_dcf(self, dcf_input: DCFInput) -> SensitivityResponse:
        base_result = self._engines[Methodology.DCF].value(dcf_input=dcf_input)
        discount_rates = DCF_DISCOUNT_RATE_RANGE
        growth_rates = DCF_GROWTH_RATE_RANGE
        data_points: list[SensitivityPoint] = []
        for dr in discount_rates:
            for gr in growth_rates:
                if dr <= dcf_input.terminal_growth_rate:
                    continue
                try:
                    modified = DCFInput.model_validate({**dcf_input.model_dump(), "discount_rate": dr, "growth_rate": gr})
                    result = self._engines[Methodology.DCF].value(dcf_input=modified)
                    data_points.append(SensitivityPoint(
                        parameters={"discount_rate": dr, "growth_rate": gr},
                        estimated_value=result.estimated_value,
                    ))
                except ValueError:
                    continue
        return SensitivityResponse(
            methodology=Methodology.DCF,
            base_estimated_value=base_result.estimated_value,
            varied_parameters=["discount_rate", "growth_rate"],
            data_points=data_points,
        )

    def _sensitivity_comps(self, sector: str, comps_input: CompsInput) -> SensitivityResponse:
        base_result = self._engines[Methodology.COMPS].value(sector=sector, comps_input=comps_input)
        steps = SENSITIVITY_STEPS
        data_points: list[SensitivityPoint] = []
        for step in steps:
            adjusted_revenue = comps_input.revenue * (1 + step)
            modified = CompsInput.model_validate({**comps_input.model_dump(), "revenue": adjusted_revenue})
            result = self._engines[Methodology.COMPS].value(sector=sector, comps_input=modified)
            data_points.append(SensitivityPoint(
                parameters={"revenue": adjusted_revenue},
                estimated_value=result.estimated_value,
            ))
        return SensitivityResponse(
            methodology=Methodology.COMPS,
            base_estimated_value=base_result.estimated_value,
            varied_parameters=["revenue"],
            data_points=data_points,
        )

    def _sensitivity_last_round(self, last_round_input: LastRoundInput) -> SensitivityResponse:
        base_result = self._engines[Methodology.LAST_ROUND].value(last_round_input=last_round_input)
        steps = SENSITIVITY_STEPS
        data_points: list[SensitivityPoint] = []
        for step in steps:
            adjusted_val = last_round_input.post_money_valuation * (1 + step)
            modified = LastRoundInput.model_validate({**last_round_input.model_dump(), "post_money_valuation": adjusted_val})
            result = self._engines[Methodology.LAST_ROUND].value(last_round_input=modified)
            data_points.append(SensitivityPoint(
                parameters={"post_money_valuation": adjusted_val},
                estimated_value=result.estimated_value,
            ))
        return SensitivityResponse(
            methodology=Methodology.LAST_ROUND,
            base_estimated_value=base_result.estimated_value,
            varied_parameters=["post_money_valuation"],
            data_points=data_points,
        )

    def _run_method(self, method: Methodology, request: ValuationRequest) -> ValuationResult:
        if method == Methodology.COMPS:
            return self._engines[method].value(
                sector=request.sector,
                comps_input=request.comps_input,
            )
        elif method == Methodology.DCF:
            return self._engines[method].value(dcf_input=request.dcf_input)
        elif method == Methodology.LAST_ROUND:
            return self._engines[method].value(last_round_input=request.last_round_input)
        else:
            raise ValueError(f"Unknown methodology: {method}")
