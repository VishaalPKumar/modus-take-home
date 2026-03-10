import pytest
from datetime import date
from app.models import (
    Methodology,
    CompsInput,
    DCFInput,
    LastRoundInput,
    ValuationRequest,
    ValuationStep,
    ValuationResult,
    ValuationReport,
)


def test_valuation_request_comps():
    req = ValuationRequest(
        company_name="Basis AI",
        sector="technology",
        methodologies=[Methodology.COMPS],
        comps_input=CompsInput(revenue=10_000_000),
    )
    assert req.company_name == "Basis AI"
    assert req.methodologies == [Methodology.COMPS]


def test_valuation_request_dcf():
    req = ValuationRequest(
        company_name="Inflo",
        sector="fintech",
        methodologies=[Methodology.DCF],
        dcf_input=DCFInput(
            revenue=5_000_000,
            growth_rate=0.20,
            discount_rate=0.10,
            terminal_growth_rate=0.03,
            projection_years=5,
        ),
    )
    assert req.dcf_input.growth_rate == 0.20


def test_valuation_request_last_round():
    req = ValuationRequest(
        company_name="TechCo",
        sector="technology",
        methodologies=[Methodology.LAST_ROUND],
        last_round_input=LastRoundInput(
            post_money_valuation=50_000_000,
            round_date=date(2024, 6, 15),
        ),
    )
    assert req.last_round_input.post_money_valuation == 50_000_000


def test_valuation_request_all_methods():
    req = ValuationRequest(
        company_name="MultiCo",
        sector="healthcare",
        methodologies=[Methodology.COMPS, Methodology.DCF, Methodology.LAST_ROUND],
        comps_input=CompsInput(revenue=20_000_000),
        dcf_input=DCFInput(revenue=20_000_000, growth_rate=0.15),
        last_round_input=LastRoundInput(
            post_money_valuation=100_000_000,
            round_date=date(2025, 1, 1),
        ),
    )
    assert len(req.methodologies) == 3


def test_valuation_result():
    result = ValuationResult(
        methodology=Methodology.COMPS,
        estimated_value=80_000_000,
        value_range=(60_000_000, 100_000_000),
        assumptions={"ev_revenue_multiple": 8.0, "peer_count": 5},
        steps=[
            ValuationStep(
                description="Filtered comparable companies by sector",
                detail="Found 5 companies in technology sector",
            )
        ],
        citations=["Mock comparable company dataset"],
    )
    assert result.estimated_value == 80_000_000
    assert len(result.steps) == 1


def test_valuation_report():
    result = ValuationResult(
        methodology=Methodology.COMPS,
        estimated_value=80_000_000,
        value_range=(60_000_000, 100_000_000),
        assumptions={"ev_revenue_multiple": 8.0},
        steps=[],
        citations=[],
    )
    report = ValuationReport(
        company_name="Basis AI",
        sector="technology",
        results=[result],
    )
    assert report.company_name == "Basis AI"
    assert len(report.results) == 1
    assert report.id is not None


def test_valuation_report_created_at_utc():
    report = ValuationReport(
        company_name="Test",
        sector="technology",
        results=[],
    )
    assert report.created_at.tzinfo is not None


def test_valuation_request_missing_comps_input_raises():
    with pytest.raises(ValueError, match="comps_input is required"):
        ValuationRequest(
            company_name="TestCo",
            sector="technology",
            methodologies=[Methodology.COMPS],
        )


def test_valuation_request_missing_dcf_input_raises():
    with pytest.raises(ValueError, match="dcf_input is required"):
        ValuationRequest(
            company_name="TestCo",
            sector="technology",
            methodologies=[Methodology.DCF],
        )


def test_valuation_request_missing_last_round_input_raises():
    with pytest.raises(ValueError, match="last_round_input is required"):
        ValuationRequest(
            company_name="TestCo",
            sector="technology",
            methodologies=[Methodology.LAST_ROUND],
        )
