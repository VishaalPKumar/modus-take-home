from datetime import date

import pytest

from app.engines.last_round import LastRoundEngine
from app.data.provider import MockDataProvider
from app.models import LastRoundInput, Methodology


def test_last_round_basic():
    engine = LastRoundEngine(MockDataProvider())
    result = engine.value(
        last_round_input=LastRoundInput(
            post_money_valuation=50_000_000,
            round_date=date(2024, 1, 1),
        ),
    )
    assert result.methodology == Methodology.LAST_ROUND
    assert result.estimated_value > 0
    assert len(result.steps) >= 3
    assert "index_return" in result.assumptions


def test_last_round_market_up():
    """If market went up since the round, valuation should increase."""
    engine = LastRoundEngine(MockDataProvider())
    result = engine.value(
        last_round_input=LastRoundInput(
            post_money_valuation=50_000_000,
            round_date=date(2023, 1, 1),  # Market was lower then
        ),
    )
    # Nasdaq went up from ~10,466 to ~20,820, so value should roughly double
    assert result.estimated_value > 50_000_000


def test_last_round_range():
    engine = LastRoundEngine(MockDataProvider())
    result = engine.value(
        last_round_input=LastRoundInput(
            post_money_valuation=100_000_000,
            round_date=date(2025, 1, 1),
        ),
    )
    assert result.value_range[0] < result.estimated_value < result.value_range[1]


def test_last_round_explicit_as_of_date():
    """Using an explicit as_of_date makes the result deterministic."""
    engine = LastRoundEngine(MockDataProvider())
    result = engine.value(
        last_round_input=LastRoundInput(
            post_money_valuation=50_000_000,
            round_date=date(2024, 1, 1),
        ),
        as_of_date=date(2025, 1, 1),
    )
    assert result.methodology == Methodology.LAST_ROUND
    assert result.estimated_value > 0
    # Running again with the same as_of_date should produce the same value
    result2 = engine.value(
        last_round_input=LastRoundInput(
            post_money_valuation=50_000_000,
            round_date=date(2024, 1, 1),
        ),
        as_of_date=date(2025, 1, 1),
    )
    assert result.estimated_value == result2.estimated_value


def test_last_round_ancient_date_raises():
    engine = LastRoundEngine(MockDataProvider())
    with pytest.raises(ValueError, match="Unable to retrieve Nasdaq index data"):
        engine.value(
            last_round_input=LastRoundInput(
                post_money_valuation=50_000_000,
                round_date=date(2015, 1, 1),
            ),
        )
