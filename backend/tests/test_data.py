from datetime import date
from app.data.provider import MockDataProvider


def test_get_comparable_companies_by_sector():
    provider = MockDataProvider()
    comps = provider.get_comparable_companies("technology")
    assert len(comps) >= 3
    for comp in comps:
        assert "name" in comp
        assert "revenue" in comp
        assert "enterprise_value" in comp
        assert "sector" in comp
        assert comp["sector"] == "technology"


def test_get_comparable_companies_unknown_sector():
    provider = MockDataProvider()
    comps = provider.get_comparable_companies("underwater_basket_weaving")
    assert comps == []


def test_get_index_value():
    provider = MockDataProvider()
    value = provider.get_index_value("nasdaq", date(2025, 1, 1))
    assert value is not None
    assert value > 0


def test_get_index_value_interpolates():
    """Should return closest available data point."""
    provider = MockDataProvider()
    value = provider.get_index_value("nasdaq", date(2025, 1, 15))
    assert value is not None


def test_get_index_value_unknown_index():
    provider = MockDataProvider()
    value = provider.get_index_value("nonexistent", date(2025, 1, 1))
    assert value is None


def test_get_index_value_far_outside_range_returns_none():
    provider = MockDataProvider()
    value = provider.get_index_value("nasdaq", date(2015, 1, 1))
    assert value is None


def test_get_sectors():
    provider = MockDataProvider()
    sectors = provider.get_sectors()
    assert "technology" in sectors
    assert len(sectors) >= 3
