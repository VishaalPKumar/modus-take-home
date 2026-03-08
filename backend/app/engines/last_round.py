from datetime import date

from app.data.provider import DataProvider
from app.engines.base import ValuationEngine
from app.models import LastRoundInput, Methodology, ValuationResult, ValuationStep


class LastRoundEngine(ValuationEngine):
    def __init__(self, data_provider: DataProvider):
        self.data_provider = data_provider

    def value(self, last_round_input: LastRoundInput) -> ValuationResult:
        steps: list[ValuationStep] = []
        today = date.today()

        # Step 1: Get index values
        round_index = self.data_provider.get_index_value("nasdaq", last_round_input.round_date)
        current_index = self.data_provider.get_index_value("nasdaq", today)

        if round_index is None or current_index is None:
            raise ValueError("Unable to retrieve Nasdaq index data for the specified dates")

        steps.append(ValuationStep(
            description="Retrieved Nasdaq Composite index values",
            detail=(
                f"Index at round date ({last_round_input.round_date}): {round_index:,.0f}, "
                f"Index today ({today}): {current_index:,.0f}"
            ),
        ))

        # Step 2: Compute return
        index_return = (current_index - round_index) / round_index

        steps.append(ValuationStep(
            description="Calculated market index return since last round",
            detail=f"Return = ({current_index:,.0f} - {round_index:,.0f}) / {round_index:,.0f} = {index_return:.2%}",
        ))

        # Step 3: Apply to valuation
        estimated_value = last_round_input.post_money_valuation * (1 + index_return)

        steps.append(ValuationStep(
            description="Applied market return to last round valuation",
            detail=(
                f"${last_round_input.post_money_valuation:,.0f} x (1 + {index_return:.2%}) = "
                f"${estimated_value:,.0f}"
            ),
        ))

        # Range: +/- 15% (illiquidity and company-specific uncertainty)
        low = estimated_value * 0.85
        high = estimated_value * 1.15

        return ValuationResult(
            methodology=Methodology.LAST_ROUND,
            estimated_value=round(estimated_value, 2),
            value_range=(round(low, 2), round(high, 2)),
            assumptions={
                "post_money_valuation": last_round_input.post_money_valuation,
                "round_date": str(last_round_input.round_date),
                "index_name": "Nasdaq Composite",
                "index_at_round": round_index,
                "index_current": current_index,
                "index_return": round(index_return, 4),
            },
            steps=steps,
            citations=[
                "Last funding round valuation (provided by user)",
                "Nasdaq Composite index data (mock dataset)",
            ],
        )
