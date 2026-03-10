# VC Audit Tool

A backend service with web frontend for estimating the fair value of private, illiquid portfolio companies in VC portfolios. Built for auditors who need a structured, traceable valuation workflow.

## Approach

**Strategy pattern** with three valuation methodologies behind a shared interface:

- **Comparable Company Analysis** — finds public comps by sector, computes median EV/Revenue multiple, applies to target
- **Discounted Cash Flow** — projects cash flows, applies WACC discount, adds Gordon Growth terminal value
- **Last Round (Market-Adjusted)** — adjusts last funding round valuation by Nasdaq index performance

Each methodology produces a structured audit trail: step-by-step derivation, key assumptions, and data citations. Users can run multiple methods simultaneously for triangulation.

**Triangulation view** — when multiple methods run, a side-by-side comparison table and range bar visualization show where estimates converge or diverge.

**Sensitivity analysis** — each result card has a "Show Sensitivity" button that varies key inputs (discount rate × growth rate for DCF, revenue for Comps, post-money valuation for Last Round) and displays a heatmap/table of outcomes.

## Key Design Decisions

- **Mock data with abstraction layer** — `DataProvider` ABC makes it trivial to swap in live APIs. Mock data keeps demos reliable.
- **Pydantic models** — single source of truth for validation, serialization, and API docs.

## Adding a Methodology

1. Add a variant to `Methodology` enum in `models.py`
2. Add an input model (e.g. `NewInput`) and wire it as an optional field on `ValuationRequest` — the existing `@model_validator` enforces that selected methods have matching inputs
3. Create `engines/new_engine.py` implementing the `ValuationEngine` ABC (one method: `value()`)
4. Register it in `ValuationService.__init__`'s `_engines` dict and add the dispatch branch in `_run_method()`
5. Add a `_sensitivity_new()` method in `ValuationService` and wire it in `sensitivity()` — vary the key input parameter(s) and call the engine's `.value()` for each
6. Add tests — see `test_comps.py` and `test_sensitivity.py` for the patterns

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
- Plug in live market data via DataProvider interface
- PDF export of valuation reports
- User authentication for multi-auditor workflows
