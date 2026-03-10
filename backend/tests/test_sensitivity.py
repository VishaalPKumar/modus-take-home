import pytest

from app.models import (
    CompsInput,
    DCFInput,
    LastRoundInput,
    Methodology,
    SensitivityRequest,
)


def test_dcf_sensitivity_returns_grid(service):
    request = SensitivityRequest(
        methodology=Methodology.DCF,
        dcf_input=DCFInput(revenue=10_000_000),
    )
    resp = service.sensitivity(request)
    assert resp.methodology == Methodology.DCF
    assert resp.varied_parameters == ["discount_rate", "growth_rate"]
    assert len(resp.data_points) > 10  # 2D grid should have many points

    # Higher discount rate → lower value (holding growth constant)
    by_dr = {}
    for pt in resp.data_points:
        gr = pt.parameters["growth_rate"]
        if gr == 0.15:  # default growth rate
            by_dr[pt.parameters["discount_rate"]] = pt.estimated_value
    sorted_drs = sorted(by_dr.keys())
    if len(sorted_drs) >= 2:
        assert by_dr[sorted_drs[0]] > by_dr[sorted_drs[-1]]


def test_comps_sensitivity_varies_revenue(service):
    request = SensitivityRequest(
        methodology=Methodology.COMPS,
        sector="technology",
        comps_input=CompsInput(revenue=10_000_000),
    )
    resp = service.sensitivity(request)
    assert resp.methodology == Methodology.COMPS
    assert resp.varied_parameters == ["revenue"]
    assert len(resp.data_points) == 7  # -30% to +30% in 10% steps

    # Value should be proportional to revenue
    values = [pt.estimated_value for pt in resp.data_points]
    assert values == sorted(values)


def test_last_round_sensitivity_varies_valuation(service):
    request = SensitivityRequest(
        methodology=Methodology.LAST_ROUND,
        last_round_input=LastRoundInput(
            post_money_valuation=50_000_000,
            round_date="2024-06-01",
        ),
    )
    resp = service.sensitivity(request)
    assert resp.methodology == Methodology.LAST_ROUND
    assert resp.varied_parameters == ["post_money_valuation"]
    assert len(resp.data_points) == 7

    # Value should be proportional to post-money valuation
    values = [pt.estimated_value for pt in resp.data_points]
    assert values == sorted(values)


def test_sensitivity_missing_input_rejects():
    with pytest.raises(Exception):
        SensitivityRequest(
            methodology=Methodology.DCF,
            # missing dcf_input
        )
