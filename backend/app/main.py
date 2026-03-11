import logging
import os
import re
from collections import OrderedDict

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from app.data.provider import MockDataProvider
from app.models import SensitivityRequest, SensitivityResponse, ValuationReport, ValuationRequest
from app.pdf import generate_report_pdf
from app.service import ValuationService

logging.basicConfig(
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

app = FastAPI(title="VC Audit Tool", version="0.1.0")

cors_origins = os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

@app.exception_handler(Exception)
def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


data_provider = MockDataProvider()
valuation_service = ValuationService(data_provider)

MAX_REPORTS = int(os.environ.get("MAX_REPORTS", "1000"))

# In-memory store for retrieving past reports (bounded, evicts oldest on overflow)
_reports: OrderedDict[str, ValuationReport] = OrderedDict()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/methodologies")
def get_methodologies() -> list[dict]:
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
def get_sectors() -> list[str]:
    return data_provider.get_sectors()


@app.post("/api/valuations", response_model=ValuationReport)
def create_valuation(request: ValuationRequest):
    try:
        report = valuation_service.run(request)
    except ValueError as e:
        logger.warning("Valuation rejected: %s", e)
        raise HTTPException(status_code=400, detail=str(e))
    _reports[report.id] = report
    while len(_reports) > MAX_REPORTS:
        _reports.popitem(last=False)
    return report


@app.post("/api/sensitivity", response_model=SensitivityResponse)
def run_sensitivity(request: SensitivityRequest):
    try:
        return valuation_service.sensitivity(request)
    except ValueError as e:
        logger.warning("Sensitivity rejected: %s", e)
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/valuations/{report_id}", response_model=ValuationReport)
def get_valuation(report_id: str):
    report = _reports.get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@app.get("/api/valuations/{report_id}/export")
def export_valuation(report_id: str):
    report = _reports.get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    pdf_bytes = generate_report_pdf(report)
    safe_name = re.sub(r"[^\w]", "_", report.company_name)
    filename = f"{safe_name}_{report_id[:8]}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
