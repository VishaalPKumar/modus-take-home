# VC Audit Tool

A full-stack service for estimating the fair value of private, illiquid portfolio companies in VC portfolios. Built for auditors who need structured, traceable valuations.

## Approach

**Strategy pattern** with three valuation methodologies behind a shared interface:

- **Comparable Company Analysis** — public comps by sector, median EV/Revenue multiple applied to target
- **Discounted Cash Flow** — projected cash flows discounted by WACC with Gordon Growth terminal value
- **Last Round (Market-Adjusted)** — last funding round valuation adjusted by Nasdaq index performance

Each methodology produces a structured audit trail: step-by-step derivation, assumptions, and citations. Run multiple methods simultaneously for **triangulation** (side-by-side comparison with range visualization). Each result includes **sensitivity analysis** varying key inputs. **PDF export** captures the full valuation report.

## Design Decisions

- **Mock data with abstraction layer** — `DataProvider` ABC makes it trivial to swap in live APIs (Bloomberg, PitchBook) without changing engine or service code
- **Pydantic models** — single source of truth for validation, serialization, and API docs. Sensitivity analysis uses `model_validate()` to ensure all cross-field validators run on modified inputs
- **Strategy pattern (`**kwargs`)** — each engine declares only its own parameters; callers dispatch uniformly without a union input type. Tradeoff: runtime argument checking, mitigated by small engine count and high test coverage
- **Sensitivity analysis** — each method varies its most impactful inputs over named constant grids (e.g. discount rate + growth rate for DCF)
- **Triangulation** — multiple methods produce convergence/divergence visualization with range bars and overlap zone
- **PDF export** — `fpdf2` generates a self-contained report with explicit per-key formatting for assumptions (currency, percent, count)
- **Security hardening** — restricted CORS methods/headers, global exception handler to suppress stack traces, input length bounds on string fields

## Tradeoffs

| Decision | Why | Limitation |
|----------|-----|------------|
| Mock data only | `DataProvider` ABC is the seam for live APIs | No real market data |
| `**kwargs` dispatch | Simpler strategy pattern | Runtime, not compile-time, arg checking |
| In-memory storage | `OrderedDict` with bounded eviction | Needs Redis/Postgres for production; process-local (not safe for multi-worker) |
| Sync endpoints | Valuations are fast (<50ms); sync `def` lets FastAPI auto-thread | No background task support |

## Future Improvements

- Live market data (Bloomberg, PitchBook, Capital IQ) · Database persistence with auth · EV/EBITDA multiples · Custom peer lists · Monte Carlo simulation · Portfolio-level batch reporting

## Adding a Methodology

1. Add variant to `Methodology` enum → 2. Add input model on `ValuationRequest` → 3. Implement `ValuationEngine` ABC → 4. Register in `ValuationService._engines` → 5. Add `_sensitivity_*()` method → 6. Add tests

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
