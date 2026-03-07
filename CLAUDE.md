# Modus Take Home

## What This Is

Take-home code review prep for Modus Audit software engineering role. The "Take Home Review" meeting on **Wed Mar 11, 2026 at 4:30-5:15 PM EDT** is a code walkthrough of the solution submitted after the tech screen.

## Context

- **Company:** Modus Audit (modusaudit.com)
- **Role:** Software Engineer
- **Interviewers:** Pranav Pillai (pranav.pillai@modusaudit.com) + Alex Wang (alex.wang@modusaudit.com)
- **Meeting:** Zoom — https://us06web.zoom.us/j/83349267988?pwd=GD1zVNih4M1UBhuaJo6CwaEbQjPUOB.1
- **Reschedule:** https://calendly.com/reschedulings/88cb5573-0f3a-4cdc-bb99-99fb52c3448b

## Take-Home Assignment: VC Audit Tool

**Timeline:** 24-48 hours
**Deliverables:** Working code in public GitHub repo + short README (max 1 page)
**Follow-up:** 30-min walkthrough interview (Mar 11) covering design, reasoning, and technical implementation

### Problem
Build a backend service that helps auditors estimate the fair value of **private, illiquid portfolio companies** in VC portfolios. The system should ingest data, apply a valuation methodology, and produce an auditable fair value estimate.

### Methodologies (pick one or more)
1. **Comparable Company Analysis (Comps)** — find public comps, apply EV/Revenue or similar multiple
2. **Discounted Cash Flow (DCF)** — project future cash flows, discount to present value (WACC)
3. **Last Round (Market-Adjusted)** — start from last funding round valuation, adjust by public index performance

### Inputs
- Portfolio company name (e.g., "Basis AI", "Inflo")
- Key data per methodology (sector/revenue for Comps, financial projections for DCF, last round valuation + date for Last Round)

### Outputs
- Estimated fair value (numeric or range)
- Key inputs and assumptions used
- Citations/data sources
- Explanation of how estimate was derived (auditable narrative)

### Core Expectations
- Backend service: input → valuation output
- **Strong code quality, organization, documentation**
- Clear workflow: data ingestion → valuation logic → output
- **Traceable, auditable process**

### Preferred
- Structured, modular design
- Graceful error handling for external data (mocking OK)
- Thoughtful UX — CLI or simple web frontend
- Wireframes/sketches acceptable

### Not Required
- Extensive deployment setup
- Highly accurate financial modeling (logic > numbers)

## Key Files

- `Modus_VC_Audit_Tool_Assignment.pdf` — full assignment spec

## Vault Note

- [[07 Projects/Modus Take Home.md]]
- [[06 Career & Education/Career/Job Search/Modus Audit.md]]
