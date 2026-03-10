from statistics import median, quantiles

from app.data.provider import DataProvider
from app.engines.base import ValuationEngine
from app.models import CompsInput, Methodology, ValuationResult, ValuationStep


class CompsEngine(ValuationEngine):
    def __init__(self, data_provider: DataProvider):
        self.data_provider = data_provider

    def value(self, sector: str, comps_input: CompsInput) -> ValuationResult:
        steps: list[ValuationStep] = []

        # Step 1: Fetch comparable companies
        comps = self.data_provider.get_comparable_companies(sector)
        if len(comps) < 2:
            raise ValueError(
                f"Need at least 2 comparable companies for sector '{sector}', found {len(comps)}"
            )

        steps.append(ValuationStep(
            description="Identified comparable public companies",
            detail=f"Found {len(comps)} companies in the {sector} sector: {', '.join(c['name'] for c in comps)}",
        ))

        # Step 2: Compute EV/Revenue multiples
        multiples = []
        for comp in comps:
            m = comp["enterprise_value"] / comp["revenue"]
            multiples.append({"name": comp["name"], "ev_revenue": round(m, 2)})

        steps.append(ValuationStep(
            description="Calculated EV/Revenue multiples for each comparable",
            detail="; ".join(f"{m['name']}: {m['ev_revenue']}x" for m in multiples),
        ))

        # Step 3: Compute median multiple
        multiple_values = [m["ev_revenue"] for m in multiples]
        median_multiple = round(median(multiple_values), 2)

        steps.append(ValuationStep(
            description="Computed median EV/Revenue multiple",
            detail=f"Median of {len(multiple_values)} multiples = {median_multiple}x",
        ))

        # Step 4: Apply to target company
        estimated_value = comps_input.revenue * median_multiple

        # Range: use 25th/75th percentile multiples
        q1, _q2, q3 = quantiles(multiple_values, n=4)
        low = comps_input.revenue * q1
        high = comps_input.revenue * q3

        steps.append(ValuationStep(
            description="Applied median multiple to target company revenue",
            detail=f"${comps_input.revenue:,.0f} x {median_multiple}x = ${estimated_value:,.0f}",
        ))

        return ValuationResult(
            methodology=Methodology.COMPS,
            estimated_value=round(estimated_value, 2),
            value_range=(round(low, 2), round(high, 2)),
            assumptions={
                "median_ev_revenue_multiple": median_multiple,
                "peer_count": len(comps),
                "target_revenue": comps_input.revenue,
            },
            steps=steps,
            citations=[
                f"Comparable company data: mock dataset ({len(comps)} public companies in {sector} sector)",
            ],
        )
