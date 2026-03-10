import pytest
from datetime import date
from app.service import ValuationService
from app.data.provider import MockDataProvider
from app.models import (
    CompsInput,
    DCFInput,
    LastRoundInput,
    Methodology,
    ValuationRequest,
)


@pytest.fixture
def service():
    return ValuationService(MockDataProvider())


def test_single_method_comps(service):
    request = ValuationRequest(
        company_name="TestCo",
        sector="technology",
        methodologies=[Methodology.COMPS],
        comps_input=CompsInput(revenue=10_000_000),
    )
    report = service.run(request)
    assert report.company_name == "TestCo"
    assert len(report.results) == 1
    assert report.results[0].methodology == Methodology.COMPS


def test_all_methods(service):
    request = ValuationRequest(
        company_name="MultiCo",
        sector="technology",
        methodologies=[Methodology.COMPS, Methodology.DCF, Methodology.LAST_ROUND],
        comps_input=CompsInput(revenue=10_000_000),
        dcf_input=DCFInput(revenue=10_000_000),
        last_round_input=LastRoundInput(
            post_money_valuation=50_000_000,
            round_date=date(2024, 6, 1),
        ),
    )
    report = service.run(request)
    assert len(report.results) == 3
    methods = {r.methodology for r in report.results}
    assert methods == {Methodology.COMPS, Methodology.DCF, Methodology.LAST_ROUND}


def test_missing_input_raises(service):
    """Model-level validation now catches missing inputs at construction time."""
    from pydantic import ValidationError

    with pytest.raises(ValidationError, match="comps_input"):
        ValuationRequest(
            company_name="BadCo",
            sector="technology",
            methodologies=[Methodology.COMPS],
            # Missing comps_input
        )
