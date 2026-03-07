# VC Audit Tool Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a backend service + web frontend that values private portfolio companies using Comps, DCF, and Last Round methodologies with full audit traceability.

**Architecture:** Strategy pattern — shared `ValuationEngine` ABC, one implementation per methodology, orchestrated by `ValuationService`. FastAPI backend with Pydantic models. React + Tailwind frontend.

**Tech Stack:** Python 3.11, FastAPI, Pydantic, uv, pytest | React, TypeScript, Tailwind CSS, Vite

---

## Task 1: Project Scaffolding — Backend

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/tests/__init__.py`

**Step 1: Initialize backend project with uv**

```bash
cd /Users/vishaalkumar/Projects/modus-take-home
mkdir -p backend/app backend/tests
```

**Step 2: Create pyproject.toml**

Create `backend/pyproject.toml`:
```toml
[project]
name = "vc-audit-tool"
version = "0.1.0"
description = "VC portfolio company fair value estimation tool"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.34.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "httpx>=0.28.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**Step 3: Create minimal FastAPI app**

Create `backend/app/__init__.py` (empty).

Create `backend/app/main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="VC Audit Tool", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}
```

Create `backend/tests/__init__.py` (empty).

**Step 4: Install dependencies and verify**

```bash
cd /Users/vishaalkumar/Projects/modus-take-home/backend
uv sync --all-extras
uv run uvicorn app.main:app --port 8000 &
curl http://localhost:8000/api/health
# Expected: {"status":"ok"}
kill %1
```

**Step 5: Commit**

```bash
git init
git add backend/
git commit -m "feat: scaffold backend with FastAPI and health endpoint"
```

---

## Task 2: Pydantic Models

**Files:**
- Create: `backend/app/models.py`
- Create: `backend/tests/test_models.py`

**Step 1: Write tests for models**

Create `backend/tests/test_models.py`:
```python
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
```

**Step 2: Run tests to verify they fail**

```bash
cd /Users/vishaalkumar/Projects/modus-take-home/backend
uv run pytest tests/test_models.py -v
# Expected: FAIL — ModuleNotFoundError
```

**Step 3: Implement models**

Create `backend/app/models.py`:
```python
from datetime import date, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class Methodology(str, Enum):
    COMPS = "comps"
    DCF = "dcf"
    LAST_ROUND = "last_round"


class CompsInput(BaseModel):
    revenue: float = Field(gt=0, description="Annual revenue in USD")
    ebitda: float | None = Field(default=None, gt=0, description="Annual EBITDA in USD")


class DCFInput(BaseModel):
    revenue: float = Field(gt=0, description="Current annual revenue in USD")
    growth_rate: float = Field(default=0.15, ge=0, le=1, description="Annual revenue growth rate")
    discount_rate: float = Field(default=0.10, gt=0, le=1, description="WACC / discount rate")
    terminal_growth_rate: float = Field(default=0.03, ge=0, le=0.10, description="Terminal growth rate")
    projection_years: int = Field(default=5, ge=1, le=10, description="Number of years to project")
    profit_margin: float = Field(default=0.15, ge=-1, le=1, description="Net profit margin for FCF estimation")


class LastRoundInput(BaseModel):
    post_money_valuation: float = Field(gt=0, description="Post-money valuation from last round in USD")
    round_date: date = Field(description="Date of last funding round")


class ValuationRequest(BaseModel):
    company_name: str = Field(min_length=1, description="Name of the portfolio company")
    sector: str = Field(min_length=1, description="Industry sector")
    methodologies: list[Methodology] = Field(min_length=1, description="Valuation methods to apply")
    comps_input: CompsInput | None = None
    dcf_input: DCFInput | None = None
    last_round_input: LastRoundInput | None = None


class ValuationStep(BaseModel):
    description: str
    detail: str


class ValuationResult(BaseModel):
    methodology: Methodology
    estimated_value: float
    value_range: tuple[float, float]
    assumptions: dict[str, Any]
    steps: list[ValuationStep]
    citations: list[str]


class ValuationReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    company_name: str
    sector: str
    results: list[ValuationResult]
    created_at: datetime = Field(default_factory=datetime.now)
```

**Step 4: Run tests to verify they pass**

```bash
cd /Users/vishaalkumar/Projects/modus-take-home/backend
uv run pytest tests/test_models.py -v
# Expected: all PASS
```

**Step 5: Commit**

```bash
git add backend/app/models.py backend/tests/test_models.py
git commit -m "feat: add Pydantic models for valuation request/response"
```

---

## Task 3: Mock Data Provider

**Files:**
- Create: `backend/app/data/__init__.py`
- Create: `backend/app/data/provider.py`
- Create: `backend/app/data/mock_data.py`
- Create: `backend/tests/test_data.py`

**Step 1: Write tests for data provider**

Create `backend/tests/test_data.py`:
```python
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


def test_get_sectors():
    provider = MockDataProvider()
    sectors = provider.get_sectors()
    assert "technology" in sectors
    assert len(sectors) >= 3
```

**Step 2: Run tests to verify they fail**

```bash
cd /Users/vishaalkumar/Projects/modus-take-home/backend
uv run pytest tests/test_data.py -v
# Expected: FAIL
```

**Step 3: Implement mock data**

Create `backend/app/data/__init__.py` (empty).

Create `backend/app/data/mock_data.py`:
```python
from datetime import date

COMPARABLE_COMPANIES = [
    # Technology
    {"name": "Datadog", "sector": "technology", "revenue": 2_130_000_000, "ebitda": 450_000_000, "enterprise_value": 38_000_000_000},
    {"name": "Snowflake", "sector": "technology", "revenue": 2_810_000_000, "ebitda": -120_000_000, "enterprise_value": 55_000_000_000},
    {"name": "CrowdStrike", "sector": "technology", "revenue": 3_060_000_000, "ebitda": 520_000_000, "enterprise_value": 70_000_000_000},
    {"name": "Palantir", "sector": "technology", "revenue": 2_220_000_000, "ebitda": 390_000_000, "enterprise_value": 50_000_000_000},
    {"name": "MongoDB", "sector": "technology", "revenue": 1_680_000_000, "ebitda": 80_000_000, "enterprise_value": 18_000_000_000},
    # Fintech
    {"name": "Bill Holdings", "sector": "fintech", "revenue": 1_180_000_000, "ebitda": 150_000_000, "enterprise_value": 15_000_000_000},
    {"name": "Marqeta", "sector": "fintech", "revenue": 480_000_000, "ebitda": -30_000_000, "enterprise_value": 3_200_000_000},
    {"name": "Toast", "sector": "fintech", "revenue": 3_870_000_000, "ebitda": 200_000_000, "enterprise_value": 14_000_000_000},
    {"name": "Shift4", "sector": "fintech", "revenue": 2_700_000_000, "ebitda": 480_000_000, "enterprise_value": 8_500_000_000},
    # Healthcare
    {"name": "Veeva Systems", "sector": "healthcare", "revenue": 2_360_000_000, "ebitda": 900_000_000, "enterprise_value": 33_000_000_000},
    {"name": "Doximity", "sector": "healthcare", "revenue": 470_000_000, "ebitda": 210_000_000, "enterprise_value": 7_500_000_000},
    {"name": "Certara", "sector": "healthcare", "revenue": 360_000_000, "ebitda": 100_000_000, "enterprise_value": 3_800_000_000},
    {"name": "Phreesia", "sector": "healthcare", "revenue": 400_000_000, "ebitda": 20_000_000, "enterprise_value": 2_800_000_000},
    # Enterprise SaaS
    {"name": "Atlassian", "sector": "enterprise_saas", "revenue": 4_400_000_000, "ebitda": 600_000_000, "enterprise_value": 50_000_000_000},
    {"name": "HubSpot", "sector": "enterprise_saas", "revenue": 2_630_000_000, "ebitda": 350_000_000, "enterprise_value": 28_000_000_000},
    {"name": "Freshworks", "sector": "enterprise_saas", "revenue": 720_000_000, "ebitda": 40_000_000, "enterprise_value": 5_200_000_000},
]

# Monthly Nasdaq Composite values (approximate, for mock purposes)
NASDAQ_INDEX: dict[str, list[tuple[date, float]]] = {
    "nasdaq": [
        (date(2023, 1, 1), 10_466),
        (date(2023, 4, 1), 12_227),
        (date(2023, 7, 1), 14_346),
        (date(2023, 10, 1), 13_219),
        (date(2024, 1, 1), 15_011),
        (date(2024, 4, 1), 15_927),
        (date(2024, 7, 1), 17_871),
        (date(2024, 10, 1), 18_095),
        (date(2025, 1, 1), 19_310),
        (date(2025, 4, 1), 18_750),
        (date(2025, 7, 1), 19_890),
        (date(2025, 10, 1), 20_150),
        (date(2026, 1, 1), 20_580),
        (date(2026, 3, 1), 20_820),
    ],
}
```

Create `backend/app/data/provider.py`:
```python
from abc import ABC, abstractmethod
from datetime import date

from app.data.mock_data import COMPARABLE_COMPANIES, NASDAQ_INDEX


class DataProvider(ABC):
    @abstractmethod
    def get_comparable_companies(self, sector: str) -> list[dict]:
        ...

    @abstractmethod
    def get_index_value(self, index_name: str, as_of_date: date) -> float | None:
        ...

    @abstractmethod
    def get_sectors(self) -> list[str]:
        ...


class MockDataProvider(DataProvider):
    def get_comparable_companies(self, sector: str) -> list[dict]:
        return [c for c in COMPARABLE_COMPANIES if c["sector"] == sector.lower()]

    def get_index_value(self, index_name: str, as_of_date: date) -> float | None:
        data_points = NASDAQ_INDEX.get(index_name.lower())
        if not data_points:
            return None
        # Find closest date
        closest = min(data_points, key=lambda dp: abs((dp[0] - as_of_date).days))
        return closest[1]

    def get_sectors(self) -> list[str]:
        return sorted(set(c["sector"] for c in COMPARABLE_COMPANIES))
```

**Step 4: Run tests**

```bash
cd /Users/vishaalkumar/Projects/modus-take-home/backend
uv run pytest tests/test_data.py -v
# Expected: all PASS
```

**Step 5: Commit**

```bash
git add backend/app/data/ backend/tests/test_data.py
git commit -m "feat: add mock data provider with comparable companies and index data"
```

---

## Task 4: Valuation Engine — Base + Comps

**Files:**
- Create: `backend/app/engines/__init__.py`
- Create: `backend/app/engines/base.py`
- Create: `backend/app/engines/comps.py`
- Create: `backend/tests/test_comps.py`

**Step 1: Write tests for CompsEngine**

Create `backend/tests/test_comps.py`:
```python
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
    with pytest.raises(ValueError, match="No comparable companies"):
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
    # The median EV/Revenue multiple should be recorded in assumptions
    assert "median_ev_revenue_multiple" in result.assumptions
    assert result.assumptions["median_ev_revenue_multiple"] > 0
```

**Step 2: Run tests to verify they fail**

```bash
cd /Users/vishaalkumar/Projects/modus-take-home/backend
uv run pytest tests/test_comps.py -v
# Expected: FAIL
```

**Step 3: Implement base engine and CompsEngine**

Create `backend/app/engines/__init__.py` (empty).

Create `backend/app/engines/base.py`:
```python
from abc import ABC, abstractmethod

from app.models import ValuationResult


class ValuationEngine(ABC):
    @abstractmethod
    def value(self, **kwargs) -> ValuationResult:
        ...
```

Create `backend/app/engines/comps.py`:
```python
from statistics import median

from app.data.provider import DataProvider
from app.engines.base import ValuationEngine
from app.models import CompsInput, Methodology, ValuationResult, ValuationStep


class CompsEngine(ValuationEngine):
    def __init__(self, data_provider: DataProvider):
        self.data_provider = data_provider

    def value(self, sector: str, comps_input: CompsInput) -> ValuationResult:
        steps: list[ValuationStep] = []

        # Step 1: Fetch comparable companies
        comps = self.data_provider.get_comparable_companies(sector)
        if not comps:
            raise ValueError(f"No comparable companies found for sector '{sector}'")

        steps.append(ValuationStep(
            description="Identified comparable public companies",
            detail=f"Found {len(comps)} companies in the {sector} sector: {', '.join(c['name'] for c in comps)}",
        ))

        # Step 2: Compute EV/Revenue multiples
        multiples = []
        for comp in comps:
            m = comp["enterprise_value"] / comp["revenue"]
            multiples.append({"name": comp["name"], "ev_revenue": round(m, 2)})

        steps.append(ValuationStep(
            description="Calculated EV/Revenue multiples for each comparable",
            detail="; ".join(f"{m['name']}: {m['ev_revenue']}x" for m in multiples),
        ))

        # Step 3: Compute median multiple
        multiple_values = [m["ev_revenue"] for m in multiples]
        median_multiple = round(median(multiple_values), 2)

        steps.append(ValuationStep(
            description="Computed median EV/Revenue multiple",
            detail=f"Median of {len(multiple_values)} multiples = {median_multiple}x",
        ))

        # Step 4: Apply to target company
        estimated_value = comps_input.revenue * median_multiple

        # Range: use 25th/75th percentile multiples
        sorted_multiples = sorted(multiple_values)
        q1_idx = len(sorted_multiples) // 4
        q3_idx = (3 * len(sorted_multiples)) // 4
        low = comps_input.revenue * sorted_multiples[q1_idx]
        high = comps_input.revenue * sorted_multiples[q3_idx]

        steps.append(ValuationStep(
            description="Applied median multiple to target company revenue",
            detail=f"${comps_input.revenue:,.0f} x {median_multiple}x = ${estimated_value:,.0f}",
        ))

        return ValuationResult(
            methodology=Methodology.COMPS,
            estimated_value=round(estimated_value, 2),
            value_range=(round(low, 2), round(high, 2)),
            assumptions={
                "median_ev_revenue_multiple": median_multiple,
                "peer_count": len(comps),
                "target_revenue": comps_input.revenue,
            },
            steps=steps,
            citations=[
                f"Comparable company data: mock dataset ({len(comps)} public companies in {sector} sector)",
            ],
        )
```

**Step 4: Run tests**

```bash
cd /Users/vishaalkumar/Projects/modus-take-home/backend
uv run pytest tests/test_comps.py -v
# Expected: all PASS
```

**Step 5: Commit**

```bash
git add backend/app/engines/ backend/tests/test_comps.py
git commit -m "feat: add ValuationEngine base class and CompsEngine"
```

---

## Task 5: DCF Engine

**Files:**
- Create: `backend/app/engines/dcf.py`
- Create: `backend/tests/test_dcf.py`

**Step 1: Write tests**

Create `backend/tests/test_dcf.py`:
```python
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
```

**Step 2: Run tests to verify they fail**

```bash
cd /Users/vishaalkumar/Projects/modus-take-home/backend
uv run pytest tests/test_dcf.py -v
# Expected: FAIL
```

**Step 3: Implement DCFEngine**

Create `backend/app/engines/dcf.py`:
```python
from app.engines.base import ValuationEngine
from app.models import DCFInput, Methodology, ValuationResult, ValuationStep


class DCFEngine(ValuationEngine):
    def value(self, dcf_input: DCFInput) -> ValuationResult:
        steps: list[ValuationStep] = []

        revenue = dcf_input.revenue
        growth_rate = dcf_input.growth_rate
        discount_rate = dcf_input.discount_rate
        terminal_growth_rate = dcf_input.terminal_growth_rate
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
```

**Step 4: Run tests**

```bash
cd /Users/vishaalkumar/Projects/modus-take-home/backend
uv run pytest tests/test_dcf.py -v
# Expected: all PASS
```

**Step 5: Commit**

```bash
git add backend/app/engines/dcf.py backend/tests/test_dcf.py
git commit -m "feat: add DCF valuation engine"
```

---

## Task 6: Last Round Engine

**Files:**
- Create: `backend/app/engines/last_round.py`
- Create: `backend/tests/test_last_round.py`

**Step 1: Write tests**

Create `backend/tests/test_last_round.py`:
```python
from datetime import date
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
```

**Step 2: Run tests to verify they fail**

```bash
cd /Users/vishaalkumar/Projects/modus-take-home/backend
uv run pytest tests/test_last_round.py -v
# Expected: FAIL
```

**Step 3: Implement LastRoundEngine**

Create `backend/app/engines/last_round.py`:
```python
from datetime import date

from app.data.provider import DataProvider
from app.engines.base import ValuationEngine
from app.models import LastRoundInput, Methodology, ValuationResult, ValuationStep


class LastRoundEngine(ValuationEngine):
    def __init__(self, data_provider: DataProvider):
        self.data_provider = data_provider

    def value(self, last_round_input: LastRoundInput) -> ValuationResult:
        steps: list[ValuationStep] = []
        today = date.today()

        # Step 1: Get index values
        round_index = self.data_provider.get_index_value("nasdaq", last_round_input.round_date)
        current_index = self.data_provider.get_index_value("nasdaq", today)

        if round_index is None or current_index is None:
            raise ValueError("Unable to retrieve Nasdaq index data for the specified dates")

        steps.append(ValuationStep(
            description="Retrieved Nasdaq Composite index values",
            detail=(
                f"Index at round date ({last_round_input.round_date}): {round_index:,.0f}, "
                f"Index today ({today}): {current_index:,.0f}"
            ),
        ))

        # Step 2: Compute return
        index_return = (current_index - round_index) / round_index

        steps.append(ValuationStep(
            description="Calculated market index return since last round",
            detail=f"Return = ({current_index:,.0f} - {round_index:,.0f}) / {round_index:,.0f} = {index_return:.2%}",
        ))

        # Step 3: Apply to valuation
        estimated_value = last_round_input.post_money_valuation * (1 + index_return)

        steps.append(ValuationStep(
            description="Applied market return to last round valuation",
            detail=(
                f"${last_round_input.post_money_valuation:,.0f} x (1 + {index_return:.2%}) = "
                f"${estimated_value:,.0f}"
            ),
        ))

        # Range: +/- 15% (illiquidity and company-specific uncertainty)
        low = estimated_value * 0.85
        high = estimated_value * 1.15

        return ValuationResult(
            methodology=Methodology.LAST_ROUND,
            estimated_value=round(estimated_value, 2),
            value_range=(round(low, 2), round(high, 2)),
            assumptions={
                "post_money_valuation": last_round_input.post_money_valuation,
                "round_date": str(last_round_input.round_date),
                "index_name": "Nasdaq Composite",
                "index_at_round": round_index,
                "index_current": current_index,
                "index_return": round(index_return, 4),
            },
            steps=steps,
            citations=[
                "Last funding round valuation (provided by user)",
                "Nasdaq Composite index data (mock dataset)",
            ],
        )
```

**Step 4: Run tests**

```bash
cd /Users/vishaalkumar/Projects/modus-take-home/backend
uv run pytest tests/test_last_round.py -v
# Expected: all PASS
```

**Step 5: Commit**

```bash
git add backend/app/engines/last_round.py backend/tests/test_last_round.py
git commit -m "feat: add Last Round (market-adjusted) valuation engine"
```

---

## Task 7: Valuation Service (Orchestrator)

**Files:**
- Create: `backend/app/service.py`
- Create: `backend/tests/test_service.py`

**Step 1: Write tests**

Create `backend/tests/test_service.py`:
```python
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
    request = ValuationRequest(
        company_name="BadCo",
        sector="technology",
        methodologies=[Methodology.COMPS],
        # Missing comps_input
    )
    with pytest.raises(ValueError, match="comps_input"):
        service.run(request)
```

**Step 2: Run tests to verify they fail**

```bash
cd /Users/vishaalkumar/Projects/modus-take-home/backend
uv run pytest tests/test_service.py -v
# Expected: FAIL
```

**Step 3: Implement ValuationService**

Create `backend/app/service.py`:
```python
from app.data.provider import DataProvider
from app.engines.comps import CompsEngine
from app.engines.dcf import DCFEngine
from app.engines.last_round import LastRoundEngine
from app.models import Methodology, ValuationReport, ValuationRequest, ValuationResult


class ValuationService:
    def __init__(self, data_provider: DataProvider):
        self.data_provider = data_provider
        self._engines = {
            Methodology.COMPS: CompsEngine(data_provider),
            Methodology.DCF: DCFEngine(),
            Methodology.LAST_ROUND: LastRoundEngine(data_provider),
        }

    def run(self, request: ValuationRequest) -> ValuationReport:
        results: list[ValuationResult] = []

        for method in request.methodologies:
            result = self._run_method(method, request)
            results.append(result)

        return ValuationReport(
            company_name=request.company_name,
            sector=request.sector,
            results=results,
        )

    def _run_method(self, method: Methodology, request: ValuationRequest) -> ValuationResult:
        if method == Methodology.COMPS:
            if not request.comps_input:
                raise ValueError("comps_input is required for Comparable Company Analysis")
            return self._engines[method].value(
                sector=request.sector,
                comps_input=request.comps_input,
            )
        elif method == Methodology.DCF:
            if not request.dcf_input:
                raise ValueError("dcf_input is required for Discounted Cash Flow analysis")
            return self._engines[method].value(dcf_input=request.dcf_input)
        elif method == Methodology.LAST_ROUND:
            if not request.last_round_input:
                raise ValueError("last_round_input is required for Last Round valuation")
            return self._engines[method].value(last_round_input=request.last_round_input)
        else:
            raise ValueError(f"Unknown methodology: {method}")
```

**Step 4: Run tests**

```bash
cd /Users/vishaalkumar/Projects/modus-take-home/backend
uv run pytest tests/test_service.py -v
# Expected: all PASS
```

**Step 5: Commit**

```bash
git add backend/app/service.py backend/tests/test_service.py
git commit -m "feat: add ValuationService orchestrator"
```

---

## Task 8: API Routes

**Files:**
- Modify: `backend/app/main.py`
- Create: `backend/tests/test_api.py`

**Step 1: Write API tests**

Create `backend/tests/test_api.py`:
```python
import pytest
from datetime import date
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200


def test_get_methodologies(client):
    resp = client.get("/api/methodologies")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
    names = {m["id"] for m in data}
    assert names == {"comps", "dcf", "last_round"}


def test_post_valuation_comps(client):
    resp = client.post("/api/valuations", json={
        "company_name": "TestCo",
        "sector": "technology",
        "methodologies": ["comps"],
        "comps_input": {"revenue": 10000000},
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["company_name"] == "TestCo"
    assert len(data["results"]) == 1
    assert data["results"][0]["methodology"] == "comps"
    assert data["results"][0]["estimated_value"] > 0


def test_post_valuation_all_methods(client):
    resp = client.post("/api/valuations", json={
        "company_name": "MultiCo",
        "sector": "technology",
        "methodologies": ["comps", "dcf", "last_round"],
        "comps_input": {"revenue": 10000000},
        "dcf_input": {"revenue": 10000000},
        "last_round_input": {
            "post_money_valuation": 50000000,
            "round_date": "2024-06-01",
        },
    })
    assert resp.status_code == 200
    assert len(resp.json()["results"]) == 3


def test_post_valuation_missing_input(client):
    resp = client.post("/api/valuations", json={
        "company_name": "BadCo",
        "sector": "technology",
        "methodologies": ["comps"],
    })
    assert resp.status_code == 400


def test_get_sectors(client):
    resp = client.get("/api/sectors")
    assert resp.status_code == 200
    data = resp.json()
    assert "technology" in data
```

**Step 2: Run tests to verify they fail**

```bash
cd /Users/vishaalkumar/Projects/modus-take-home/backend
uv run pytest tests/test_api.py -v
# Expected: FAIL (routes don't exist yet)
```

**Step 3: Implement routes**

Replace `backend/app/main.py` with:
```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.data.provider import MockDataProvider
from app.models import Methodology, ValuationReport, ValuationRequest
from app.service import ValuationService

app = FastAPI(title="VC Audit Tool", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

data_provider = MockDataProvider()
valuation_service = ValuationService(data_provider)

# In-memory store for retrieving past reports
_reports: dict[str, ValuationReport] = {}


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/methodologies")
def get_methodologies():
    return [
        {
            "id": "comps",
            "name": "Comparable Company Analysis",
            "description": "Values a company by comparing to similar public companies using EV/Revenue multiples.",
            "required_fields": ["sector", "revenue"],
        },
        {
            "id": "dcf",
            "name": "Discounted Cash Flow",
            "description": "Projects future cash flows and discounts them to present value.",
            "required_fields": ["revenue", "growth_rate", "discount_rate"],
        },
        {
            "id": "last_round",
            "name": "Last Round (Market-Adjusted)",
            "description": "Adjusts last funding round valuation by public market index performance.",
            "required_fields": ["post_money_valuation", "round_date"],
        },
    ]


@app.get("/api/sectors")
def get_sectors():
    return data_provider.get_sectors()


@app.post("/api/valuations", response_model=ValuationReport)
def create_valuation(request: ValuationRequest):
    try:
        report = valuation_service.run(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    _reports[report.id] = report
    return report


@app.get("/api/valuations/{report_id}", response_model=ValuationReport)
def get_valuation(report_id: str):
    report = _reports.get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report
```

**Step 4: Run tests**

```bash
cd /Users/vishaalkumar/Projects/modus-take-home/backend
uv run pytest tests/test_api.py -v
# Expected: all PASS
```

**Step 5: Run all backend tests**

```bash
cd /Users/vishaalkumar/Projects/modus-take-home/backend
uv run pytest -v
# Expected: all PASS
```

**Step 6: Commit**

```bash
git add backend/app/main.py backend/tests/test_api.py
git commit -m "feat: add API routes for valuations, methodologies, and sectors"
```

---

## Task 9: Frontend Scaffolding

**Files:**
- Create: `frontend/` (Vite + React + TypeScript + Tailwind)

**Step 1: Scaffold with Vite**

```bash
cd /Users/vishaalkumar/Projects/modus-take-home
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm install -D tailwindcss @tailwindcss/vite
```

**Step 2: Configure Tailwind**

Update `frontend/vite.config.ts`:
```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
});
```

Replace `frontend/src/index.css` with:
```css
@import "tailwindcss";
```

**Step 3: Verify it runs**

```bash
cd /Users/vishaalkumar/Projects/modus-take-home/frontend
npm run dev &
curl -s http://localhost:5173 | head -5
# Expected: HTML response
kill %1
```

**Step 4: Commit**

```bash
cd /Users/vishaalkumar/Projects/modus-take-home
git add frontend/
git commit -m "feat: scaffold React + Tailwind frontend with Vite"
```

---

## Task 10: Frontend — API Client & Types

**Files:**
- Create: `frontend/src/types.ts`
- Create: `frontend/src/api.ts`

**Step 1: Create TypeScript types matching backend models**

Create `frontend/src/types.ts`:
```typescript
export type Methodology = "comps" | "dcf" | "last_round";

export interface CompsInput {
  revenue: number;
  ebitda?: number;
}

export interface DCFInput {
  revenue: number;
  growth_rate?: number;
  discount_rate?: number;
  terminal_growth_rate?: number;
  projection_years?: number;
  profit_margin?: number;
}

export interface LastRoundInput {
  post_money_valuation: number;
  round_date: string; // ISO date string
}

export interface ValuationRequest {
  company_name: string;
  sector: string;
  methodologies: Methodology[];
  comps_input?: CompsInput;
  dcf_input?: DCFInput;
  last_round_input?: LastRoundInput;
}

export interface ValuationStep {
  description: string;
  detail: string;
}

export interface ValuationResult {
  methodology: Methodology;
  estimated_value: number;
  value_range: [number, number];
  assumptions: Record<string, unknown>;
  steps: ValuationStep[];
  citations: string[];
}

export interface ValuationReport {
  id: string;
  company_name: string;
  sector: string;
  results: ValuationResult[];
  created_at: string;
}

export interface MethodologyInfo {
  id: Methodology;
  name: string;
  description: string;
  required_fields: string[];
}
```

**Step 2: Create API client**

Create `frontend/src/api.ts`:
```typescript
import { ValuationRequest, ValuationReport, MethodologyInfo } from "./types";

const BASE_URL = "/api";

export async function runValuation(
  request: ValuationRequest
): Promise<ValuationReport> {
  const resp = await fetch(`${BASE_URL}/valuations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!resp.ok) {
    const error = await resp.json().catch(() => ({ detail: resp.statusText }));
    throw new Error(error.detail || "Valuation failed");
  }
  return resp.json();
}

export async function getMethodologies(): Promise<MethodologyInfo[]> {
  const resp = await fetch(`${BASE_URL}/methodologies`);
  return resp.json();
}

export async function getSectors(): Promise<string[]> {
  const resp = await fetch(`${BASE_URL}/sectors`);
  return resp.json();
}
```

**Step 3: Commit**

```bash
git add frontend/src/types.ts frontend/src/api.ts
git commit -m "feat: add TypeScript types and API client for frontend"
```

---

## Task 11: Frontend — Input Form Component

**Files:**
- Create: `frontend/src/components/ValuationForm.tsx`

**Step 1: Build the form**

Create `frontend/src/components/ValuationForm.tsx`:
```tsx
import { useState } from "react";
import { Methodology, ValuationRequest } from "../types";

interface Props {
  sectors: string[];
  onSubmit: (request: ValuationRequest) => void;
  loading: boolean;
}

export default function ValuationForm({ sectors, onSubmit, loading }: Props) {
  const [companyName, setCompanyName] = useState("");
  const [sector, setSector] = useState("");
  const [methods, setMethods] = useState<Set<Methodology>>(new Set());

  // Comps
  const [revenue, setRevenue] = useState("");

  // DCF
  const [dcfRevenue, setDcfRevenue] = useState("");
  const [growthRate, setGrowthRate] = useState("15");
  const [discountRate, setDiscountRate] = useState("10");
  const [terminalGrowthRate, setTerminalGrowthRate] = useState("3");
  const [profitMargin, setProfitMargin] = useState("15");

  // Last Round
  const [postMoneyValuation, setPostMoneyValuation] = useState("");
  const [roundDate, setRoundDate] = useState("");

  const toggleMethod = (m: Methodology) => {
    const next = new Set(methods);
    if (next.has(m)) next.delete(m);
    else next.add(m);
    setMethods(next);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const request: ValuationRequest = {
      company_name: companyName,
      sector,
      methodologies: Array.from(methods),
    };

    if (methods.has("comps")) {
      request.comps_input = { revenue: parseFloat(revenue) };
    }
    if (methods.has("dcf")) {
      request.dcf_input = {
        revenue: parseFloat(dcfRevenue || revenue),
        growth_rate: parseFloat(growthRate) / 100,
        discount_rate: parseFloat(discountRate) / 100,
        terminal_growth_rate: parseFloat(terminalGrowthRate) / 100,
        profit_margin: parseFloat(profitMargin) / 100,
      };
    }
    if (methods.has("last_round")) {
      request.last_round_input = {
        post_money_valuation: parseFloat(postMoneyValuation),
        round_date: roundDate,
      };
    }

    onSubmit(request);
  };

  const inputClass =
    "w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500";
  const labelClass = "block text-sm font-medium text-gray-700 mb-1";

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label className={labelClass}>Company Name</label>
        <input
          className={inputClass}
          value={companyName}
          onChange={(e) => setCompanyName(e.target.value)}
          placeholder="e.g., Basis AI"
          required
        />
      </div>

      <div>
        <label className={labelClass}>Sector</label>
        <select
          className={inputClass}
          value={sector}
          onChange={(e) => setSector(e.target.value)}
          required
        >
          <option value="">Select a sector</option>
          {sectors.map((s) => (
            <option key={s} value={s}>
              {s.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className={labelClass}>Valuation Methodologies</label>
        <div className="space-y-2">
          {(
            [
              ["comps", "Comparable Company Analysis"],
              ["dcf", "Discounted Cash Flow"],
              ["last_round", "Last Round (Market-Adjusted)"],
            ] as [Methodology, string][]
          ).map(([id, name]) => (
            <label key={id} className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={methods.has(id)}
                onChange={() => toggleMethod(id)}
                className="rounded border-gray-300"
              />
              {name}
            </label>
          ))}
        </div>
      </div>

      {methods.has("comps") && (
        <fieldset className="rounded-md border border-gray-200 p-4 space-y-3">
          <legend className="text-sm font-semibold text-gray-600 px-1">
            Comparable Company Analysis
          </legend>
          <div>
            <label className={labelClass}>Annual Revenue ($)</label>
            <input
              className={inputClass}
              type="number"
              value={revenue}
              onChange={(e) => setRevenue(e.target.value)}
              placeholder="e.g., 10000000"
              required
            />
          </div>
        </fieldset>
      )}

      {methods.has("dcf") && (
        <fieldset className="rounded-md border border-gray-200 p-4 space-y-3">
          <legend className="text-sm font-semibold text-gray-600 px-1">
            Discounted Cash Flow
          </legend>
          <div>
            <label className={labelClass}>Annual Revenue ($)</label>
            <input
              className={inputClass}
              type="number"
              value={dcfRevenue || revenue}
              onChange={(e) => setDcfRevenue(e.target.value)}
              placeholder="e.g., 10000000"
              required
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className={labelClass}>Growth Rate (%)</label>
              <input
                className={inputClass}
                type="number"
                value={growthRate}
                onChange={(e) => setGrowthRate(e.target.value)}
                step="0.1"
              />
            </div>
            <div>
              <label className={labelClass}>Discount Rate / WACC (%)</label>
              <input
                className={inputClass}
                type="number"
                value={discountRate}
                onChange={(e) => setDiscountRate(e.target.value)}
                step="0.1"
              />
            </div>
            <div>
              <label className={labelClass}>Terminal Growth (%)</label>
              <input
                className={inputClass}
                type="number"
                value={terminalGrowthRate}
                onChange={(e) => setTerminalGrowthRate(e.target.value)}
                step="0.1"
              />
            </div>
            <div>
              <label className={labelClass}>Profit Margin (%)</label>
              <input
                className={inputClass}
                type="number"
                value={profitMargin}
                onChange={(e) => setProfitMargin(e.target.value)}
                step="0.1"
              />
            </div>
          </div>
        </fieldset>
      )}

      {methods.has("last_round") && (
        <fieldset className="rounded-md border border-gray-200 p-4 space-y-3">
          <legend className="text-sm font-semibold text-gray-600 px-1">
            Last Round (Market-Adjusted)
          </legend>
          <div>
            <label className={labelClass}>Post-Money Valuation ($)</label>
            <input
              className={inputClass}
              type="number"
              value={postMoneyValuation}
              onChange={(e) => setPostMoneyValuation(e.target.value)}
              placeholder="e.g., 50000000"
              required
            />
          </div>
          <div>
            <label className={labelClass}>Round Date</label>
            <input
              className={inputClass}
              type="date"
              value={roundDate}
              onChange={(e) => setRoundDate(e.target.value)}
              required
            />
          </div>
        </fieldset>
      )}

      <button
        type="submit"
        disabled={loading || methods.size === 0}
        className="w-full rounded-md bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
      >
        {loading ? "Running Valuation..." : "Run Valuation"}
      </button>
    </form>
  );
}
```

**Step 2: Commit**

```bash
git add frontend/src/components/ValuationForm.tsx
git commit -m "feat: add ValuationForm component"
```

---

## Task 12: Frontend — Results Display Component

**Files:**
- Create: `frontend/src/components/ValuationResults.tsx`

**Step 1: Build the results component**

Create `frontend/src/components/ValuationResults.tsx`:
```tsx
import { ValuationReport, ValuationResult } from "../types";

const methodNames: Record<string, string> = {
  comps: "Comparable Company Analysis",
  dcf: "Discounted Cash Flow",
  last_round: "Last Round (Market-Adjusted)",
};

function formatCurrency(value: number): string {
  if (value >= 1_000_000_000) return `$${(value / 1_000_000_000).toFixed(1)}B`;
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `$${(value / 1_000).toFixed(0)}K`;
  return `$${value.toFixed(0)}`;
}

function ResultCard({ result }: { result: ValuationResult }) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">
          {methodNames[result.methodology]}
        </h3>
        <span className="text-2xl font-bold text-blue-600">
          {formatCurrency(result.estimated_value)}
        </span>
      </div>

      <div className="text-sm text-gray-500">
        Range: {formatCurrency(result.value_range[0])} —{" "}
        {formatCurrency(result.value_range[1])}
      </div>

      {/* Assumptions */}
      <div>
        <h4 className="text-sm font-semibold text-gray-700 mb-2">
          Key Assumptions
        </h4>
        <div className="rounded-md bg-gray-50 p-3">
          <dl className="grid grid-cols-2 gap-x-4 gap-y-1 text-sm">
            {Object.entries(result.assumptions).map(([key, value]) => (
              <div key={key} className="contents">
                <dt className="text-gray-500">
                  {key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
                </dt>
                <dd className="text-gray-900 font-medium">
                  {typeof value === "number"
                    ? value > 1000
                      ? formatCurrency(value)
                      : value
                    : String(value)}
                </dd>
              </div>
            ))}
          </dl>
        </div>
      </div>

      {/* Derivation Steps */}
      <div>
        <h4 className="text-sm font-semibold text-gray-700 mb-2">
          Audit Trail
        </h4>
        <ol className="space-y-2">
          {result.steps.map((step, i) => (
            <li key={i} className="text-sm">
              <div className="flex gap-2">
                <span className="flex-shrink-0 w-5 h-5 rounded-full bg-blue-100 text-blue-700 text-xs flex items-center justify-center font-medium">
                  {i + 1}
                </span>
                <div>
                  <p className="font-medium text-gray-800">
                    {step.description}
                  </p>
                  <p className="text-gray-500 mt-0.5 whitespace-pre-wrap">
                    {step.detail}
                  </p>
                </div>
              </div>
            </li>
          ))}
        </ol>
      </div>

      {/* Citations */}
      <div>
        <h4 className="text-sm font-semibold text-gray-700 mb-1">
          Data Sources
        </h4>
        <ul className="text-sm text-gray-500 list-disc list-inside">
          {result.citations.map((c, i) => (
            <li key={i}>{c}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default function ValuationResults({
  report,
}: {
  report: ValuationReport;
}) {
  return (
    <div className="space-y-6">
      {/* Summary */}
      <div className="rounded-lg border border-blue-200 bg-blue-50 p-5">
        <h2 className="text-lg font-semibold text-gray-900 mb-1">
          Valuation Summary — {report.company_name}
        </h2>
        <p className="text-sm text-gray-500 mb-4">
          Sector: {report.sector.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())} |
          Generated: {new Date(report.created_at).toLocaleString()} |
          Report ID: {report.id.slice(0, 8)}
        </p>

        {report.results.length > 1 && (
          <div className="grid grid-cols-3 gap-4">
            {report.results.map((r) => (
              <div key={r.methodology} className="text-center">
                <p className="text-xs text-gray-500 uppercase tracking-wide">
                  {methodNames[r.methodology]}
                </p>
                <p className="text-xl font-bold text-blue-600 mt-1">
                  {formatCurrency(r.estimated_value)}
                </p>
                <p className="text-xs text-gray-400">
                  {formatCurrency(r.value_range[0])} – {formatCurrency(r.value_range[1])}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Per-method details */}
      {report.results.map((result) => (
        <ResultCard key={result.methodology} result={result} />
      ))}
    </div>
  );
}
```

**Step 2: Commit**

```bash
git add frontend/src/components/ValuationResults.tsx
git commit -m "feat: add ValuationResults display component"
```

---

## Task 13: Frontend — Wire It All Together (App.tsx)

**Files:**
- Modify: `frontend/src/App.tsx`

**Step 1: Implement App.tsx**

Replace `frontend/src/App.tsx` with:
```tsx
import { useState, useEffect } from "react";
import ValuationForm from "./components/ValuationForm";
import ValuationResults from "./components/ValuationResults";
import { runValuation, getSectors } from "./api";
import { ValuationRequest, ValuationReport } from "./types";

export default function App() {
  const [sectors, setSectors] = useState<string[]>([]);
  const [report, setReport] = useState<ValuationReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getSectors().then(setSectors).catch(console.error);
  }, []);

  const handleSubmit = async (request: ValuationRequest) => {
    setLoading(true);
    setError(null);
    try {
      const result = await runValuation(request);
      setReport(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto max-w-7xl px-6 py-4">
          <h1 className="text-xl font-bold text-gray-900">VC Audit Tool</h1>
          <p className="text-sm text-gray-500">
            Fair value estimation for private portfolio companies
          </p>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Input Panel */}
          <div className="lg:col-span-4">
            <div className="sticky top-8 rounded-lg border border-gray-200 bg-white p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Company Details
              </h2>
              <ValuationForm
                sectors={sectors}
                onSubmit={handleSubmit}
                loading={loading}
              />
            </div>
          </div>

          {/* Results Panel */}
          <div className="lg:col-span-8">
            {error && (
              <div className="rounded-md bg-red-50 border border-red-200 p-4 mb-6">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}
            {report ? (
              <ValuationResults report={report} />
            ) : (
              <div className="rounded-lg border-2 border-dashed border-gray-200 p-12 text-center">
                <p className="text-gray-400 text-sm">
                  Select methodologies and run a valuation to see results
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
```

**Step 2: Clean up boilerplate**

Remove `frontend/src/App.css` (not needed, using Tailwind).

**Step 3: Verify the full app works**

```bash
# Terminal 1: Start backend
cd /Users/vishaalkumar/Projects/modus-take-home/backend
uv run uvicorn app.main:app --port 8000 --reload &

# Terminal 2: Start frontend
cd /Users/vishaalkumar/Projects/modus-take-home/frontend
npm run dev &

# Wait a moment, then test
sleep 3
curl -s http://localhost:5173 | head -5
curl -s http://localhost:8000/api/health

# Kill both
kill %1 %2
```

**Step 4: Commit**

```bash
git add frontend/src/App.tsx
git rm frontend/src/App.css 2>/dev/null || true
git commit -m "feat: wire up App with form and results panels"
```

---

## Task 14: README

**Files:**
- Create: `README.md`

**Step 1: Write README**

Create `README.md` (max 1 page per assignment spec):

```markdown
# VC Audit Tool

A backend service with web frontend for estimating the fair value of private, illiquid portfolio companies in VC portfolios. Built for auditors who need a structured, traceable valuation workflow.

## Approach

**Strategy pattern** with three valuation methodologies behind a shared interface:

- **Comparable Company Analysis** — finds public comps by sector, computes median EV/Revenue multiple, applies to target
- **Discounted Cash Flow** — projects cash flows, applies WACC discount, adds Gordon Growth terminal value
- **Last Round (Market-Adjusted)** — adjusts last funding round valuation by Nasdaq index performance

Each methodology produces a structured audit trail: step-by-step derivation, key assumptions, and data citations. Users can run multiple methods simultaneously for triangulation.

## Key Design Decisions

- **Mock data with abstraction layer** — `DataProvider` ABC makes it trivial to swap in live APIs. Mock data keeps demos reliable.
- **All three methods** — demonstrates modular design; adding a new methodology = one new class implementing `ValuationEngine`.
- **Pydantic models** — single source of truth for validation, serialization, and API docs.

## Setup

```bash
# Backend
cd backend
uv sync --all-extras
uv run uvicorn app.main:app --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Testing

```bash
cd backend
uv run pytest -v
```

## Tech Stack

Python 3.11, FastAPI, Pydantic | React, TypeScript, Tailwind CSS, Vite

## If I Had More Time

- Persist reports to SQLite for historical comparison
- Add sensitivity analysis (vary discount rate / multiples and show impact)
- Plug in live market data via DataProvider interface
- PDF export of valuation reports
- User authentication for multi-auditor workflows
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README with setup instructions and design rationale"
```

---

## Task 15: Final Polish & Verification

**Step 1: Run all backend tests**

```bash
cd /Users/vishaalkumar/Projects/modus-take-home/backend
uv run pytest -v
# Expected: all PASS
```

**Step 2: Verify frontend builds**

```bash
cd /Users/vishaalkumar/Projects/modus-take-home/frontend
npm run build
# Expected: successful build
```

**Step 3: Add .gitignore**

Create `.gitignore`:
```
__pycache__/
*.pyc
.venv/
node_modules/
dist/
.env
```

**Step 4: Final commit**

```bash
git add .gitignore
git commit -m "chore: add .gitignore"
```

**Step 5: Verify git log**

```bash
git log --oneline
# Expected: clean commit history showing progressive feature development
```
