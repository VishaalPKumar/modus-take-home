import pytest

from app.engines.comps import CompsEngine
from app.data.provider import MockDataProvider
from app.models import CompsInput, Methodology


def test_comps_engine_technology():
    engine = CompsEngine(MockDataProvider())
    result = engine.value(
        sector="technology",
        comps_input=CompsInput(revenue=10_000_000),
    )
    assert result.methodology == Methodology.COMPS
    assert result.estimated_value > 0
    assert result.value_range[0] < result.estimated_value < result.value_range[1]
    assert len(result.steps) >= 3
    assert len(result.assumptions) >= 2
    assert len(result.citations) >= 1


def test_comps_engine_no_comps_found():
    engine = CompsEngine(MockDataProvider())
    with pytest.raises(ValueError, match="at least 3 comparable"):
        engine.value(
            sector="underwater_basket_weaving",
            comps_input=CompsInput(revenue=10_000_000),
        )


def test_comps_engine_uses_median_multiple():
    engine = CompsEngine(MockDataProvider())
    result = engine.value(
        sector="technology",
        comps_input=CompsInput(revenue=10_000_000),
    )
    assert "median_ev_revenue_multiple" in result.assumptions
    assert result.assumptions["median_ev_revenue_multiple"] > 0


class _FewCompsProvider(MockDataProvider):
    def __init__(self, count: int):
        self._count = count

    def get_comparable_companies(self, sector: str) -> list[dict]:
        all_comps = super().get_comparable_companies(sector)
        return all_comps[: self._count]


def test_comps_few_comparables_valid_range():
    engine = CompsEngine(_FewCompsProvider(3))
    result = engine.value(sector="technology", comps_input=CompsInput(revenue=10_000_000))
    assert result.value_range[0] <= result.estimated_value <= result.value_range[1]


def test_comps_single_comparable_raises():
    engine = CompsEngine(_FewCompsProvider(1))
    with pytest.raises(ValueError, match="at least 3 comparable"):
        engine.value(sector="technology", comps_input=CompsInput(revenue=10_000_000))


def test_comps_two_comparables_raises():
    engine = CompsEngine(_FewCompsProvider(2))
    with pytest.raises(ValueError, match="at least 3 comparable"):
        engine.value(sector="technology", comps_input=CompsInput(revenue=10_000_000))
