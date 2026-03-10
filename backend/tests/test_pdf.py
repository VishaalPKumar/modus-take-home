from datetime import datetime, timezone

from app.models import ValuationReport, ValuationResult, ValuationStep
from app.pdf import generate_report_pdf


def _make_result(methodology: str, value: float) -> ValuationResult:
    return ValuationResult(
        methodology=methodology,
        estimated_value=value,
        value_range=(value * 0.8, value * 1.2),
        assumptions={"discount_rate": 0.10, "growth_rate": 0.15},
        steps=[
            ValuationStep(description="Gather inputs", detail="Collected financial data"),
            ValuationStep(description="Apply model", detail="Ran valuation model"),
        ],
        citations=["Mock data provider", "Public market data"],
    )


def test_generate_report_pdf_single_method():
    report = ValuationReport(
        id="test-1234-abcd",
        company_name="TestCo",
        sector="technology",
        results=[_make_result("dcf", 50_000_000)],
        created_at=datetime(2026, 1, 15, tzinfo=timezone.utc),
    )
    pdf_bytes = generate_report_pdf(report)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes[:5] == b"%PDF-"


def test_generate_report_pdf_multi_method():
    report = ValuationReport(
        id="test-5678-efgh",
        company_name="MultiCo",
        sector="healthcare",
        results=[
            _make_result("comps", 40_000_000),
            _make_result("dcf", 50_000_000),
            _make_result("last_round", 45_000_000),
        ],
        created_at=datetime(2026, 1, 15, tzinfo=timezone.utc),
    )
    pdf_bytes = generate_report_pdf(report)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes[:5] == b"%PDF-"
