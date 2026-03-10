import pytest

from app.engines.dcf import DCFEngine
from app.models import DCFInput, Methodology


def test_dcf_basic():
    engine = DCFEngine()
    result = engine.value(
        dcf_input=DCFInput(
            revenue=10_000_000,
            growth_rate=0.20,
            discount_rate=0.10,
            terminal_growth_rate=0.03,
            projection_years=5,
            profit_margin=0.15,
        ),
    )
    assert result.methodology == Methodology.DCF
    assert result.estimated_value > 0
    assert result.value_range[0] < result.estimated_value < result.value_range[1]
    assert len(result.steps) >= 3
    assert "discount_rate" in result.assumptions
    assert "terminal_growth_rate" in result.assumptions


def test_dcf_defaults():
    engine = DCFEngine()
    result = engine.value(dcf_input=DCFInput(revenue=5_000_000))
    assert result.estimated_value > 0
    assert result.assumptions["discount_rate"] == 0.10
    assert result.assumptions["terminal_growth_rate"] == 0.03


def test_dcf_higher_growth_means_higher_value():
    engine = DCFEngine()
    low_growth = engine.value(dcf_input=DCFInput(revenue=10_000_000, growth_rate=0.05))
    high_growth = engine.value(dcf_input=DCFInput(revenue=10_000_000, growth_rate=0.30))
    assert high_growth.estimated_value > low_growth.estimated_value


def test_dcf_equal_rates_raises():
    with pytest.raises(ValueError, match="discount_rate.*must be greater than.*terminal_growth_rate"):
        DCFInput(revenue=10_000_000, discount_rate=0.05, terminal_growth_rate=0.05)


def test_dcf_terminal_exceeds_discount_raises():
    with pytest.raises(ValueError, match="discount_rate.*must be greater than.*terminal_growth_rate"):
        DCFInput(revenue=10_000_000, discount_rate=0.05, terminal_growth_rate=0.08)
