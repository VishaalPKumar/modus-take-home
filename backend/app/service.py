from app.data.provider import DataProvider
from app.engines.comps import CompsEngine
from app.engines.dcf import DCFEngine
from app.engines.last_round import LastRoundEngine
from app.models import Methodology, ValuationReport, ValuationRequest, ValuationResult


class ValuationService:
    def __init__(self, data_provider: DataProvider):
        self.data_provider = data_provider
        self._engines = {
            Methodology.COMPS: CompsEngine(data_provider),
            Methodology.DCF: DCFEngine(),
            Methodology.LAST_ROUND: LastRoundEngine(data_provider),
        }

    def run(self, request: ValuationRequest) -> ValuationReport:
        results: list[ValuationResult] = []

        for method in request.methodologies:
            result = self._run_method(method, request)
            results.append(result)

        return ValuationReport(
            company_name=request.company_name,
            sector=request.sector,
            results=results,
        )

    def _run_method(self, method: Methodology, request: ValuationRequest) -> ValuationResult:
        if method == Methodology.COMPS:
            if not request.comps_input:
                raise ValueError("comps_input is required for Comparable Company Analysis")
            return self._engines[method].value(
                sector=request.sector,
                comps_input=request.comps_input,
            )
        elif method == Methodology.DCF:
            if not request.dcf_input:
                raise ValueError("dcf_input is required for Discounted Cash Flow analysis")
            return self._engines[method].value(dcf_input=request.dcf_input)
        elif method == Methodology.LAST_ROUND:
            if not request.last_round_input:
                raise ValueError("last_round_input is required for Last Round valuation")
            return self._engines[method].value(last_round_input=request.last_round_input)
        else:
            raise ValueError(f"Unknown methodology: {method}")
