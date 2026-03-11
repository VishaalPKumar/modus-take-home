"""Shared constants used across the application."""

from app.models import Methodology

METHOD_NAMES: dict[Methodology, str] = {
    Methodology.COMPS: "Comparable Company Analysis",
    Methodology.DCF: "Discounted Cash Flow",
    Methodology.LAST_ROUND: "Last Round (Market-Adjusted)",
}

# Sensitivity analysis parameter grids
DCF_DISCOUNT_RATE_RANGE: list[float] = [r / 100 for r in range(6, 17, 2)]   # 6% to 16%
DCF_GROWTH_RATE_RANGE: list[float] = [r / 100 for r in range(5, 36, 5)]     # 5% to 35%
SENSITIVITY_STEPS: list[float] = [i / 10 for i in range(-3, 4)]             # -30% to +30%
