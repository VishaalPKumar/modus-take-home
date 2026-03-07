# VC Audit Tool — Design Document

**Date:** 2026-03-06
**Status:** Approved

## Overview

A backend service with a web frontend that helps auditors estimate the fair value of private, illiquid portfolio companies in VC portfolios. The system ingests company data, applies one or more valuation methodologies, and produces an auditable fair value estimate with full traceability.

## Decisions

- **Language/Framework:** Python + FastAPI (backend), React + Tailwind (frontend)
- **Methodologies:** All three — Comps, DCF, Last Round
- **Data:** Mock data with realistic structure and a clear abstraction layer for future API integration
- **Multi-method:** Users can run multiple methodologies on the same company and see a comparison view
- **Architecture:** Strategy pattern — shared `ValuationEngine` interface, one implementation per methodology

## Architecture

### Strategy Pattern with Audit Trail

Each valuation methodology implements a shared `ValuationEngine` abstract base class with a `value(request) -> ValuationResult` method. A `ValuationService` orchestrates running selected engines and assembles a `ValuationReport`.

```
Request -> ValuationService -> [CompsEngine, DCFEngine, LastRoundEngine] -> ValuationReport
```

### Core Domain Model

- `ValuationEngine` — ABC with `value(request) -> ValuationResult`
- `CompsEngine`, `DCFEngine`, `LastRoundEngine` — concrete implementations
- `ValuationService` — orchestrator that runs selected engines, assembles comparison
- `DataProvider` — ABC for external data; `MockDataProvider` is the concrete implementation

### Data Structures (Pydantic)

- `ValuationRequest` — company name, sector, revenue, financial projections, last round info, selected methodologies
- `ValuationResult` — per-methodology: estimated value (point + range), assumptions list, step-by-step derivation, citations
- `ValuationReport` — collection of results, summary comparison, metadata (timestamp, version)

### API Endpoints

- `POST /api/valuations` — run valuation(s) for a company
- `GET /api/valuations/{id}` — retrieve a past valuation report
- `GET /api/methodologies` — list available methodologies and their required inputs

## Frontend

Single-page app with two panels:

**Left — Input Form:**
- Company name, sector dropdown
- Methodology selector (checkboxes)
- Conditional fields per methodology:
  - Comps: revenue, optional EBITDA
  - DCF: revenue projections (5 years), growth rate, discount rate (WACC)
  - Last Round: post-money valuation, round date
- "Run Valuation" button

**Right — Results:**
- Summary card: estimated fair value (weighted average or range across methods)
- Per-methodology result cards showing:
  - Point estimate and range
  - Assumptions (table)
  - Step-by-step derivation (audit narrative)
  - Data sources / citations
- Comparison view when multiple methods selected

**Design feel:** Clean, professional, minimal — "internal audit tool" aesthetic.

## Methodology Implementations

### 1. Comparable Company Analysis (Comps)

- **Input:** sector, revenue (optionally EBITDA)
- **Mock data:** ~10-15 public companies across 3-4 sectors with revenue, EBITDA, enterprise value
- **Logic:** filter comps by sector -> compute EV/Revenue multiples -> take median -> apply to target revenue
- **Audit output:** which comps selected, their multiples, the median, the final calculation

### 2. Discounted Cash Flow (DCF)

- **Input:** 5-year revenue projections (or base revenue + growth rate), discount rate (WACC), terminal growth rate
- **Logic:** project free cash flows -> compute terminal value -> discount all to present value
- **Defaults:** 10% WACC, 3% terminal growth rate (overridable)
- **Audit output:** each year's projected cash flow, discount factor, terminal value calc, sum

### 3. Last Round (Market-Adjusted)

- **Input:** post-money valuation from last round, date of last round
- **Mock data:** historical index values (Nasdaq Composite monthly) for last 3 years
- **Logic:** compute index return from round date to today -> apply to last round valuation
- **Audit output:** index values at both dates, percentage change, adjusted valuation

## Project Structure

```
vc-audit-tool/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, CORS, routes
│   │   ├── models.py            # Pydantic request/response models
│   │   ├── service.py           # ValuationService orchestrator
│   │   ├── engines/
│   │   │   ├── base.py          # ValuationEngine ABC
│   │   │   ├── comps.py
│   │   │   ├── dcf.py
│   │   │   └── last_round.py
│   │   └── data/
│   │       ├── provider.py      # DataProvider ABC + MockDataProvider
│   │       └── mock_data.py     # Realistic mock datasets
│   ├── tests/
│   │   ├── test_comps.py
│   │   ├── test_dcf.py
│   │   ├── test_last_round.py
│   │   └── test_service.py
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   └── ...
│   ├── package.json
│   └── ...
└── README.md
```

## Testing

- Unit tests for each engine (deterministic with mock data)
- Integration test for the ValuationService orchestrator
- pytest as the test runner

## Error Handling

- Pydantic validation on all inputs
- Clear error messages for missing required fields per methodology
- Graceful handling when a methodology can't compute (e.g., no comps for sector)

---

## Alternatives Considered

### Architecture Alternatives

#### Approach B: Pipeline/Step-Based Architecture

Each methodology broken into discrete, composable pipeline steps (e.g., `FetchComps -> ComputeMultiple -> ApplyMultiple`). Each step logs its inputs and outputs for auditability.

**Why considered:** Very granular audit trail — you can see every intermediate computation. Each step is independently testable and reusable.

**Why rejected:** Over-engineered for three methods with 2-3 steps each. The pipeline abstraction adds complexity (step ordering, error propagation between steps, step registry) that doesn't pay off at this scale. The strategy pattern gives us clean separation without the indirection overhead. If we had 10+ methodologies with shared substeps, this would make more sense.

#### Approach C: Simple Functions

Each methodology as a standalone function returning a dict. No shared interface, no classes.

**Why considered:** Fastest to build. Minimal abstraction overhead.

**Why rejected:** Doesn't demonstrate the "structured, modular design" the assignment calls out. Inconsistent audit output across methods (each function would define its own return shape). Harder to add new methodologies without copy-pasting. Doesn't give interviewers much to discuss in terms of design decisions.

### Tech Stack Alternatives

#### TypeScript + Express/Hono

**Why considered:** Strong type safety, good ecosystem. Shows versatility if the team uses TS.

**Why rejected:** Python is more natural for financial/data workflows. Pydantic gives us excellent input validation and self-documenting models. FastAPI auto-generates OpenAPI docs. Less boilerplate for this problem domain.

#### Go

**Why considered:** Strong engineering signal, great performance characteristics.

**Why rejected:** Slower to iterate on for a time-boxed take-home. Less natural for financial modeling. The problem doesn't need Go's concurrency or performance strengths.

### UX Alternatives

#### CLI Only (Typer/Click)

**Why considered:** Very quick to build. Easy to demo. Shows backend focus.

**Why rejected:** The audience is auditors — they'd use a web tool. A web frontend better demonstrates understanding of the end user. The audit narrative and comparison view are more compelling visually than terminal output.

#### REST API Only (Swagger docs)

**Why considered:** Minimal scope, maximum backend focus.

**Why rejected:** The assignment calls out "thoughtful UX" as preferred. API-only might feel incomplete. FastAPI's Swagger UI is nice but doesn't communicate "I thought about how auditors would use this."

### Data Alternatives

#### Live APIs (Yahoo Finance, FMP)

**Why considered:** More impressive, shows real-world data integration.

**Why rejected:** Adds flakiness risk during a live demo. API keys and rate limits complicate setup. The assignment explicitly says mocking is fine. A clean abstraction layer (DataProvider ABC) shows we've designed for real data without the fragility.

#### Mix: Mock Comps + Live Index Data

**Why considered:** Best of both worlds — realistic market data for Last Round, controlled data for Comps.

**Why rejected:** Partial live data is the worst of both worlds for a demo — some things work offline, some don't. Keeps the "why does this need internet?" question open. Full mock is more predictable and the DataProvider abstraction shows the same design intent.
