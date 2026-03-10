# VC Audit Tool

A full-stack service for estimating the fair value of private, illiquid portfolio companies in VC portfolios. Built for auditors who need structured, traceable valuations.

## Approach

**Strategy pattern** with three valuation methodologies behind a shared interface:

- **Comparable Company Analysis** — public comps by sector, median EV/Revenue multiple applied to target
- **Discounted Cash Flow** — projected cash flows discounted by WACC with Gordon Growth terminal value
- **Last Round (Market-Adjusted)** — last funding round valuation adjusted by Nasdaq index performance

Each methodology produces a structured audit trail: step-by-step derivation, assumptions, and citations. Run multiple methods simultaneously for **triangulation** (side-by-side comparison with range visualization). Each result includes **sensitivity analysis** varying key inputs. **PDF export** captures the full valuation report.

## Design Decisions

- **Mock data with abstraction layer** — `DataProvider` ABC makes it trivial to swap in live APIs
- **Pydantic models** — single source of truth for validation, serialization, and API docs
## Adding a Methodology

1. Add a variant to `Methodology` enum in `models.py`
2. Add an input model and wire it as an optional field on `ValuationRequest`
3. Create `engines/new_engine.py` implementing the `ValuationEngine` ABC
4. Register it in `ValuationService._engines` and add the dispatch branch in `_run_method()`
5. Add a `_sensitivity_new()` method in `ValuationService` and wire it in `sensitivity()`
6. Add tests — see `test_comps.py` and `test_sensitivity.py` for patterns

## Setup

```bash
# Backend
cd backend && uv sync --all-extras
uv run uvicorn app.main:app --port 8000

# Frontend (separate terminal)
cd frontend && npm install && npm run dev
```

Open http://localhost:5173 — run tests with `cd backend && uv run pytest -v`

## Tech Stack

Python 3.11, FastAPI, Pydantic | React, TypeScript, Tailwind CSS, Vite

## Presentation

Open `presentation/presentation.html` in a browser for a slide walkthrough of the architecture and features.
