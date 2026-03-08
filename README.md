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
