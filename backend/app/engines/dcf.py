from app.engines.base import ValuationEngine
from app.models import DCFInput, Methodology, ValuationResult, ValuationStep


class DCFEngine(ValuationEngine):
    def value(self, dcf_input: DCFInput) -> ValuationResult:
        steps: list[ValuationStep] = []

        revenue = dcf_input.revenue
        growth_rate = dcf_input.growth_rate
        discount_rate = dcf_input.discount_rate
        terminal_growth_rate = dcf_input.terminal_growth_rate

        # Validate here even though DCFInput has a model_validator, because
        # model_copy() bypasses Pydantic validators on the copied instance.
        if discount_rate <= terminal_growth_rate:
            raise ValueError(
                f"Discount rate ({discount_rate}) must exceed terminal growth rate ({terminal_growth_rate}) "
                "for the Gordon Growth Model to produce a valid terminal value"
            )
        margin = dcf_input.profit_margin
        years = dcf_input.projection_years

        # Step 1: Project future cash flows
        projected_cash_flows: list[dict] = []
        for year in range(1, years + 1):
            projected_revenue = revenue * ((1 + growth_rate) ** year)
            fcf = projected_revenue * margin
            discount_factor = 1 / ((1 + discount_rate) ** year)
            pv = fcf * discount_factor
            projected_cash_flows.append({
                "year": year,
                "revenue": round(projected_revenue, 2),
                "fcf": round(fcf, 2),
                "discount_factor": round(discount_factor, 4),
                "present_value": round(pv, 2),
            })

        cf_detail = "\n".join(
            f"Year {cf['year']}: Revenue ${cf['revenue']:,.0f}, FCF ${cf['fcf']:,.0f}, "
            f"PV ${cf['present_value']:,.0f} (DF={cf['discount_factor']})"
            for cf in projected_cash_flows
        )
        steps.append(ValuationStep(
            description=f"Projected {years}-year free cash flows",
            detail=cf_detail,
        ))

        # Step 2: Compute terminal value
        final_year_fcf = projected_cash_flows[-1]["fcf"]
        terminal_value = (final_year_fcf * (1 + terminal_growth_rate)) / (discount_rate - terminal_growth_rate)
        terminal_discount_factor = 1 / ((1 + discount_rate) ** years)
        pv_terminal = terminal_value * terminal_discount_factor

        steps.append(ValuationStep(
            description="Calculated terminal value (Gordon Growth Model)",
            detail=(
                f"Terminal FCF = ${final_year_fcf * (1 + terminal_growth_rate):,.0f}, "
                f"Terminal Value = ${terminal_value:,.0f}, "
                f"PV of Terminal = ${pv_terminal:,.0f}"
            ),
        ))

        # Step 3: Sum
        pv_cash_flows = sum(cf["present_value"] for cf in projected_cash_flows)
        estimated_value = pv_cash_flows + pv_terminal

        steps.append(ValuationStep(
            description="Summed present values",
            detail=(
                f"PV of projected cash flows: ${pv_cash_flows:,.0f} + "
                f"PV of terminal value: ${pv_terminal:,.0f} = "
                f"Estimated fair value: ${estimated_value:,.0f}"
            ),
        ))

        # Range: +/- 20% sensitivity
        low = estimated_value * 0.8
        high = estimated_value * 1.2

        return ValuationResult(
            methodology=Methodology.DCF,
            estimated_value=round(estimated_value, 2),
            value_range=(round(low, 2), round(high, 2)),
            assumptions={
                "revenue": revenue,
                "growth_rate": growth_rate,
                "discount_rate": discount_rate,
                "terminal_growth_rate": terminal_growth_rate,
                "profit_margin": margin,
                "projection_years": years,
            },
            steps=steps,
            citations=["DCF model with Gordon Growth terminal value"],
        )
